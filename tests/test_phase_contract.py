"""Source-frame, rejection, cut and missing-signal regression contracts."""
import numpy as np
import pytest

from analyzer.phase_detector import PHASES, SwingPhaseDetector, NO_SWING_MESSAGE
from analyzer.video_signal import SceneCuts
from serialization import extract_representative_frames


def swing():
    return np.interp(np.arange(120), [0,25,60,70,95,119], [400,400,200,410,160,160])


def detector(signal, fps=30, cuts=()):
    det = SwingPhaseDetector(fps)
    for i,y in enumerate(signal):
        det.update(i,y,y,source_frame=i*2,time_sec=i/fps,body_scale=200)
    det.cut_frames = list(cuts)
    det.detect_all_phases()
    return det


def test_representatives_use_source_frame_not_list_position():
    fd=[]; ann=[]
    # Leading pose-only images and sparse original IDs reproduce the old drift.
    ann.append({'frame':0,'image':np.full((2,2,3),255,np.uint8)})
    for p,phase in enumerate(PHASES):
        for j in range(10):
            source=20+p*20+j*2
            fd.append({'frame':source,'phase':phase})
            ann.append({'frame':source,'image':np.full((2,2,3),p*10+j,np.uint8)})
    ann.reverse()  # arbitrary order must not affect lookup
    frames=extract_representative_frames(fd,ann)
    by_pixel={int(a['image'][0,0,0]):a['frame'] for a in ann}
    for p,phase in enumerate(PHASES):
        source=by_pixel[int(frames[phase][0,0,0])]
        assert 20+p*20 <= source <= 38+p*20
        expected=0 if phase=='임팩트' else 8 if phase=='다운스윙' else 5
        assert source==20+p*20+expected*2


def test_constant_and_jitter_are_not_swings():
    for signal in (np.full(120,400), 400+np.sin(np.arange(120)) * 3):
        assert detector(signal).phase_boundaries == {}


def test_order_and_source_clock():
    det=detector(swing())
    assert list(det.phase_boundaries)==PHASES
    last=-1
    for phase,(lo,hi) in det.phase_boundaries.items():
        assert last<lo<=hi
        assert phase in det.frame_phases[lo:hi+1]
        assert det.phase_boundaries_frames[phase]==(lo*2,hi*2)
        assert det.phase_boundaries_sec[phase]==(lo/30,hi/30)
        last=hi
    assert det.phase_boundaries_frames['임팩트'][0]==140


def test_cut_prevents_joining_two_half_swings():
    values=np.r_[np.linspace(400,200,60),np.linspace(400,450,30),np.linspace(450,200,30)]
    assert detector(values,cuts=[120]).phase_boundaries == {}
    valid=detector(np.r_[swing(),swing()],cuts=[240])
    ranges=list(valid.phase_boundaries_frames.values())
    assert all(hi<240 for lo,hi in ranges) or all(lo>=240 for lo,hi in ranges)


def test_scene_cut_is_detected_from_pixels():
    cuts=SceneCuts(30)
    assert not cuts.update(np.zeros((100,100,3),np.uint8),0)
    assert cuts.update(np.full((100,100,3),200,np.uint8),1)
    assert not cuts.update(np.full((100,100,3),200,np.uint8),2)


def test_interpolation_has_time_limit_and_cannot_cross_cut():
    y=swing();y[40:44]=np.nan
    det=detector(y)
    filled,_=det._segments()
    assert np.isfinite(filled[40:44]).all()
    y[40:55]=np.nan
    filled,_=detector(y)._segments()
    assert np.isnan(filled[40:55]).all()
    y=swing();y[40:44]=np.nan
    filled,_=detector(y,cuts=[84])._segments()
    assert np.isnan(filled[40:44]).all()


@pytest.mark.parametrize('route',['/detect-phases','/score-live'])
def test_constant_api_returns_422_without_score(client,route):
    body={'wrist_y':[400.0]*120}
    if route=='/score-live': body['frames']=[{}]*120
    res=client.post(route,json=body)
    assert res.status_code==422
    assert res.json()=={'detail':NO_SWING_MESSAGE}


def test_analyze_rejection_precedes_scoring(client,monkeypatch):
    import main
    from analyzer.phase_detector import SwingNotFoundError
    def reject(*args,**kwargs): raise SwingNotFoundError()
    def forbidden(*args,**kwargs): pytest.fail('score must not run for a rejected clip')
    monkeypatch.setattr(main,'process_video',reject)
    monkeypatch.setattr(main,'compute_score',forbidden)
    res=client.post('/analyze',files={'file':('static.mp4',b'placeholder','video/mp4')})
    assert res.status_code==422
    assert res.json()['detail']==NO_SWING_MESSAGE


def test_async_rejection_returns_422_on_poll(client):
    import jobs
    job_id=jobs.create_job()
    jobs.fail(job_id,NO_SWING_MESSAGE)
    res=client.get('/jobs/'+job_id)
    assert res.status_code==422
    assert res.json()['detail']==NO_SWING_MESSAGE


def test_long_gap_splits_cycles_without_time_compression():
    y=np.r_[swing()[:61], [np.nan]*30, swing()[61:]]
    det=detector(y)
    assert det.phase_boundaries == {}
    assert len(det.wrist_times_sec)==len(y)


def test_real_static_clip_is_rejected_by_both_endpoints(client):
    import os
    from pathlib import Path
    from analyzer.pipeline import trim_video
    video=Path(__file__).resolve().parents[1]/'golf_swing_analyzer/video/일반.mp4'
    clip=trim_video(str(video),1.0,65/30)
    try:
        data=Path(clip).read_bytes()
        for route in ('/auto-window','/analyze'):
            response=client.post(route,files={'file':('static.mp4',data,'video/mp4')})
            assert response.status_code==422
            assert response.json()['detail']==NO_SWING_MESSAGE
    finally:
        os.unlink(clip)


def test_selected_video_uses_source_ids_and_stays_before_cut():
    import os
    from pathlib import Path
    from analyzer.pipeline import process_video, trim_video
    video=Path(__file__).resolve().parents[1]/'golf_swing_analyzer/video/일반.mp4'
    clip=trim_video(str(video),1.5,9.7)
    try:
        fd,ann,_,fps,det,eff=process_video(clip,3,source_start_sec=1.5)
    finally:
        os.unlink(clip)
    assert eff==1
    assert 162 in det.cut_frames
    assert abs(det.phase_boundaries_frames['임팩트'][0]-90)<=3
    assert all(hi<162 for lo,hi in det.phase_boundaries_frames.values())
    reps=extract_representative_frames(fd,ann)
    by_image={id(a['image']):a['frame'] for a in ann}
    assert set(reps)==set(PHASES)
    for phase,im in reps.items():
        lo,hi=det.phase_boundaries_frames[phase]
        assert lo<=by_image[id(im)]<=hi
        assert det.phase_boundaries_sec[phase][0]==pytest.approx((lo-45)/fps)
    assert all(f['time']==pytest.approx((f['frame']-45)/fps) for f in fd)


def test_representative_survives_missing_angle_metrics():
    # A pose may have a visible wrist but no six-joint angle observation.
    fd=[{'frame':10,'phase':'백스윙'}]
    ann=[{'frame':3,'phase':'어드레스','image':np.zeros((2,2,3),np.uint8)},
         {'frame':10,'phase':'백스윙','image':np.ones((2,2,3),np.uint8)}]
    reps=extract_representative_frames(fd,ann)
    assert reps['어드레스'] is ann[0]['image']
    assert reps['백스윙'] is ann[1]['image']
