import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.swinglab.app',
  appName: 'Swing.Lab',
  webDir: 'dist',
  // Dev-only: keeps the app's own origin on plain http so it matches the
  // http://10.0.2.2:8010 dev API — Capacitor's default https scheme triggers
  // browser mixed-content blocking against a plain-http API.
  server: {
    androidScheme: 'http',
  },
};

export default config;
