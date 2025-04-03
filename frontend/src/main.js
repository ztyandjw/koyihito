// 使用全局Vue对象
const { createApp } = Vue;
import mitt from 'mitt';
// 导入配置
import { appConfig } from './js/wav.js';
import { messageConfig } from './js/message.js';

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

        // 修改滚动逻辑
        this.$nextTick(() => {
            const messagesContainer = document.querySelector('.messages-container');
            if (messagesContainer) {
                // 使用自定义的平滑滚动，持续时间设为1000ms（1秒）
                this.smoothScroll(
                    messagesContainer, 
                    messagesContainer.scrollHeight, 
                    1000
                );
            }
        });

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
            console.log('[AI陪練プロトコル]:', this.ja_v1);
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
        },
        // 添加平滑滚动方法
        smoothScroll(element, target, duration) {
            const start = element.scrollTop;
            const distance = target - start;
            const startTime = performance.now();

            function animation(currentTime) {
                const timeElapsed = currentTime - startTime;
                const progress = Math.min(timeElapsed / duration, 1);

                // easeInOutQuad 缓动函数
                const ease = progress => {
                    return progress < 0.5
                        ? 2 * progress * progress
                        : 1 - Math.pow(-2 * progress + 2, 2) / 2;
                };

                element.scrollTop = start + distance * ease(progress);

                if (progress < 1) {
                    requestAnimationFrame(animation);
                }
            }

            requestAnimationFrame(animation);
        }
    }
});

// 挂载应用
app.mount('#app');
