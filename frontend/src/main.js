// 使用全局Vue对象
const { createApp } = Vue;
import mitt from 'mitt';
// 导入配置
import { appConfig } from './javascript/wav.js';
import { messageConfig } from './javascript/message.js';

// 创建应用
const app = createApp({
    data() {
        return {
            ...appConfig.data(),
            ...messageConfig.data(),
            tools_v1: false
        }
    },
    mounted() {
        console.log('mounted 方法开始执行');
        app.config.globalProperties.emitter = mitt();

        this.emitter.on('stt-result', (stt_text) => {
            console.log('收到语音识别结果:', stt_text);
            const message = {
                content: stt_text,
                isOutgoing: true,
                timestamp: new Date()
            };
            // this.messages.push(message);
            //messageConfig.sendMessage(stt_text)
            this.inputValue = stt_text;
            this.sendMessage(stt_text);
        });
    },
    methods: {
        ...appConfig.methods,
        ...messageConfig.methods,
        toggleToolV1() {
            this.tools_v1 = !this.tools_v1;
            console.log('赛博苦力V1.0:', this.tools_v1);  // 在控制台输出当前状态

        }
    }
});

// 挂载应用
app.mount('#app');
