// 使用全局Vue对象
const { createApp } = Vue;

// 导入配置
import { appConfig } from './javascript/wav.js';

// 创建应用
const app = createApp(appConfig);

// 挂载应用
app.mount('#app');
