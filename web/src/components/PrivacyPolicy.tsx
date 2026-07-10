import { useI18n } from "../lib/i18n";
import styles from "./PrivacyPolicy.module.css";

interface Props {
  onBack: () => void;
}

/**
 * 개인정보처리방침 본문 — 법적 고지문이므로 서비스 언어(한국어) 고정.
 * 루트의 개인정보처리방침.md와 내용을 동기화할 것 (버전 표기 동일하게 유지).
 */
export function PrivacyPolicy({ onBack }: Props) {
  const { t } = useI18n();

  return (
    <div className={styles.wrap}>
      <button className={styles.back} onClick={onBack}>
        ← {t("privacy_back")}
      </button>
      <h2>개인정보처리방침</h2>
      <p className={styles.version}>버전 2026-07-10 (시행일: 서비스 정식 오픈일)</p>

      <h3>1. 수집하는 정보</h3>
      <ul>
        <li>계정: 이메일 주소, 암호화(단방향 해시)된 비밀번호</li>
        <li>
          스윙 영상: <strong>분석 목적으로만 일시 처리되며, 분석 완료 즉시 서버에서 삭제됩니다. 원본
          영상은 저장하지 않습니다.</strong>
        </li>
        <li>분석 결과: 점수·관절각 통계·구간 정보·대표 장면 이미지(7장) — 회원이 "결과 저장"을 선택한 경우에만 보관</li>
      </ul>

      <h3>2. 이용 목적</h3>
      <ul>
        <li>스윙 분석 결과 제공 및 회원의 분석 기록·변화 추이 표시</li>
        <li>AI 코칭 리포트 생성 — 이때 외부 AI 제공사(Google Gemini 등)에 전송되는 것은 영상이 아니라
          관절각 통계 수치(JSON)입니다</li>
      </ul>

      <h3>3. 보관 및 파기</h3>
      <ul>
        <li>업로드 영상: 분석 완료 즉시 자동 삭제 (보관하지 않음)</li>
        <li>저장된 분석 결과: 회원이 직접 삭제하거나 회원 탈퇴 시 지체 없이 파기</li>
        <li>계정 정보: 회원 탈퇴 시 지체 없이 파기</li>
      </ul>

      <h3>4. 제3자 제공</h3>
      <p>
        AI 코칭 기능 사용 시에만 관절각 통계 데이터가 선택한 AI 제공사에 전송됩니다. 그 외 어떤 정보도
        제3자에게 제공하지 않습니다.
      </p>

      <h3>5. 이용자의 권리</h3>
      <p>
        회원은 언제든지 저장된 스윙 기록을 열람·삭제할 수 있으며, "내 기록" 화면 하단의 "회원 탈퇴"로
        계정과 모든 기록을 직접 삭제할 수 있습니다. 문의: 서비스 운영자 이메일(정식 오픈 시 공지).
      </p>

      <p className={styles.note}>
        (EN) Uploaded videos are processed for analysis only and deleted immediately afterwards — originals
        are never stored. Only joint-angle statistics (not video) are sent to the AI provider when you use
        AI coaching.
      </p>
    </div>
  );
}
