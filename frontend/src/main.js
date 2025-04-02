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
            tools_v1: false,
            ja_v1: false,
            selectedLang: { code: 'zh', name: '中文' },
            langSelectorOpen: false,
            languages: [
                { code: 'zh', name: '中文' },
                { code: 'ja', name: '日本语' },
                { code: 'en', name: '英文' }
            ]
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
        },
        toggleTerminal() {
            this.ja_v1 = !this.ja_v1;
            console.log('机奴移动终端:', this.ja_v1);
        },
        toggleLangSelector(event) {
            event.stopPropagation();
            this.langSelectorOpen = !this.langSelectorOpen;
            
            if (this.langSelectorOpen) {
                setTimeout(() => {
                    document.addEventListener('click', this.closeLangSelector);
                }, 10);
            }
        },
        closeLangSelector() {
            this.langSelectorOpen = false;
            document.removeEventListener('click', this.closeLangSelector);
        },
        selectLanguage(lang) {
            this.selectedLang = lang;
            this.langSelectorOpen = false;
        }
    }
});

// 挂载应用
app.mount('#app');
