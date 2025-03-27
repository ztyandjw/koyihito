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
            },
            {
                content: '苏苏 我这就想 想得很! 都不能说我的00后钱 让我买东西好难啊!',
                isOutgoing: true,
                timestamp: new Date()
            },
            {
                content: '「温柔长情讲述头发」真是听听你跟我干了一些似乎大人也放心不出扰邻或闹？何种小小麻烦该怎么好好叙述？（微排小姨）不会下次这全是奥i没有不良想法对了吗',
                isOutgoing: false,
                timestamp: new Date()
            },
            {
                content: '(轻轻地叹地看那酒) 其是小菜爱的孩子，还记得看不到妈妈那样虽然习惯,有话想对你说...但...（请不要家就爱谁户典）不必但海朵书好厉害超过人，才能明明要多思理围饭！（减角防但一丝砂融的笑容）相应ァ咝?',
                isOutgoing: false,
                timestamp: new Date()
            }
        ];

        return {
            inputValue: '', // 输入框的值
            messages: savedMessages ? JSON.parse(savedMessages) : defaultMessages,
            currentConversationId: null // 当前会话ID
        }
    },
    methods: {
        // 发送消息方法
        async sendMessage() {
            if (!this.inputValue.trim()) return;
            
            // 创建用户消息对象
            const userMessage = {
                content: this.inputValue,
                isOutgoing: true,
                timestamp: new Date()
            };
            
            // 添加用户消息到数组
            this.messages.push(userMessage);
            
            try {
                // 准备请求数据，如果有会话ID则包含它
                const requestData = {
                    message: this.inputValue
                };
                if (this.currentConversationId) {
                    requestData.conversation_id = this.currentConversationId;
                    console.log('使用现有会话ID:', this.currentConversationId);
                }

                // 调用后端API
                const response = await fetch('/api/ollama/chat', {
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
                
                // 保存新的会话ID
                this.currentConversationId = data.conversation_id;
                console.log('保存新的会话ID:', this.currentConversationId);

                // 创建助手回复消息对象
                const assistantMessage = {
                    content: data.response,
                    isOutgoing: false,
                    timestamp: new Date()
                };

                // 添加助手回复到消息数组
                this.messages.push(assistantMessage);
                
            } catch (error) {
                console.error('发送消息失败:', error);
                this.messages.push({
                    content: '消息发送失败，请重试',
                    isOutgoing: false,
                    timestamp: new Date(),
                    isError: true
                });
            }
            
            // 保存到 localStorage
            localStorage.setItem('chatMessages', JSON.stringify(this.messages));
            
            // 清空输入框
            this.inputValue = '';

            // 滚动到最新消息
            this.$nextTick(() => {
                const messagesContainer = document.querySelector('.messages-container');
                if (messagesContainer) {
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                }
            });
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
