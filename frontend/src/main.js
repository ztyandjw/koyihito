// 使用全局Vue对象
const { createApp } = Vue;

// 导入配置
import { appConfig } from './javascript/wav.js';
import { messageConfig } from './javascript/message.js';

// 创建应用
const app = createApp({
    data() {
        return {
            ...appConfig.data(),
            ...messageConfig.data()
        }
    },
    methods: {
        ...appConfig.methods,
        ...messageConfig.methods
    }
});

// 挂载应用
app.mount('#app');
