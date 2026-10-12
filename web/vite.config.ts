import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// 발표 시연: VITE_API_BASE=/api 로 빌드하면 /api 요청을 이 Mac의 분석 서버(8010)로 넘긴다.
// 학교 PC는 ngrok 주소 하나로 화면·분석 모두 사용 (docs/DEMO_REMOTE.md)
const apiProxy = {
  '/api': {
    target: 'http://127.0.0.1:8010',
    changeOrigin: true,
    rewrite: (path: string) => path.replace(/^\/api/, ''),
  },
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  preview: { proxy: apiProxy, allowedHosts: ['.ngrok-free.app', '.ngrok-free.dev', '.ngrok.app'] },
})
