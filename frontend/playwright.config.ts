import {defineConfig} from '@playwright/test';
export default defineConfig({testDir:'./e2e',timeout:30000,workers:1,use:{baseURL:process.env.FINN_E2E_URL||'http://127.0.0.1:5173',viewport:{width:390,height:844},reducedMotion:'reduce',trace:'retain-on-failure'},reporter:[['list'],['json',{outputFile:'test-results/results.json'}]]});
