// 导出消息处理配置
export const messageConfig = {
    data() {
        // 从 localStorage 获取存储的消息和会话ID
        const savedMessages = localStorage.getItem('chatMessages');
        const defaultMessages = [
            {
                content: '欢迎小可爱注册～',
                isOutgoing: false,
                timestamp: new Date()
            }
        ];

        return {
            inputValue: '', // 输入框的值
            messages: savedMessages ? JSON.parse(savedMessages) : defaultMessages,
            currentConversationId: null, // 当前会话ID
            thinkingDots: ''
        }
    },
    beforeMount() {
        console.log('beforeMount 执行');
    },
    // 添加 mounted 钩子，在组件挂载完成时执行
    mounted() {
    
        // 第一部分：设置事件监听
        console.log('接受发送事件，emitter是否存在:', !!this.emitter);  
        

        // // 第二部分：滚动到底部
        // this.$nextTick(() => {
        //     const messagesContainer = document.querySelector('.messages-container');
        //     if (messagesContainer) {
        //         messagesContainer.scrollTop = messagesContainer.scrollHeight;
        //     }
        // });
    },
    methods: {

        


        
        // 添加一个动态更新思考点的方法
        updateThinkingDots() {
            const dots = ['...', '.. .', '. ..', ' ...'];
            let index = 0;
            return setInterval(() => {
                const thinkingMessage = this.messages.find(m => m.isThinking);
                if (thinkingMessage) {
                    thinkingMessage.content = `神经网络同步中${dots[index]}`;
                    index = (index + 1) % dots.length;
                }
            }, 500);
        },

        // 播放音频方法
        playAudio(audioUrl) {
            console.log('播放音频:', audioUrl);
            
            const audio = new Audio(audioUrl);
            
            // 尝试自动播放
            audio.play().catch(error => {
                console.error('自动播放失败:', error);
                // 如果自动播放失败，显示播放按钮
                this.showPlayButton(audioUrl);  // 使用this.调用方法
            });
        },

        // 发送消息方法
        async sendMessage() {
            if (!this.inputValue.trim()) return;
            
            // 用户消息
            const userMessage = {
                tools_v1: this.tools_v1,
                content: this.inputValue,
                isOutgoing: true,
                timestamp: new Date()
            };
            this.messages.push(userMessage);

            // 添加思考中的消息
            const thinkingMessage = {
                content: '神经网络同步中...',
                isOutgoing: false,
                isThinking: true,
                timestamp: new Date()
            };
            this.messages.push(thinkingMessage);

            // 启动思考动画
            const thinkingInterval = this.updateThinkingDots();
            
            // 清空输入并滚动到底部
            this.inputValue = '';
            this.$nextTick(() => {
                const messagesContainer = document.querySelector('.messages-container');
                if (messagesContainer) {
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                }
            });

            try {
                const requestData = {
                    ja_v1: this.ja_v1,
                    tools_v1: this.tools_v1,
                    message: userMessage.content
                };
                if (this.currentConversationId) {
                    requestData.conversation_id = this.currentConversationId;
                }

                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(requestData)
                });

                if (!response.ok) {
                    throw new Error(`API请求失败: ${response.status}`);
                }
                const data = await response.json();
                
                // 保存会话ID
                this.currentConversationId = data.conversation_id;

                // 移除思考中的消息
                this.messages = this.messages.filter(msg => !msg.isThinking);
                
                // 添加实际回复
                const assistantMessage = {
                    content: data.response,
                    isOutgoing: false,
                    timestamp: new Date()
                };
                this.messages.push(assistantMessage);
                if (data.audio_file_path) {
                    this.playAudio(data.audio_file_path);
                }

            } catch (error) {
                console.error('发送消息失败:', error);
                // 移除思考中的消息
                this.messages = this.messages.filter(msg => !msg.isThinking);
                // 添加错误消息
                this.messages.push({
                    content: '消息发送失败，请重试',
                    isOutgoing: false,
                    timestamp: new Date(),
                    isError: true
                });
            } finally {
                // 清除思考动画
                clearInterval(thinkingInterval);
                // 保存到本地存储
                localStorage.setItem('chatMessages', JSON.stringify(this.messages));
                // 滚动到底部
                this.$nextTick(() => {
                    const messagesContainer = document.querySelector('.messages-container');
                    if (messagesContainer) {
                        messagesContainer.scrollTop = messagesContainer.scrollHeight;
                    }
                });
            }
        }
    },
    // 监听消息变化，保存到 localStorage
    watch: {
        messages: {
            handler(newMessages) {
                localStorage.setItem('chatMessages', JSON.stringify(newMessages));
            },
            deep: true
        }
    }
};
