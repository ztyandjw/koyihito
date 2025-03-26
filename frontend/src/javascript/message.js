// 导出消息处理配置
export const messageConfig = {
    data() {
        // 从 localStorage 获取存储的消息，如果没有则使用默认消息
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
            messages: savedMessages ? JSON.parse(savedMessages) : defaultMessages
        }
    },
    methods: {
        // 发送消息方法
        sendMessage() {
            // 检查输入值是否为空
            if (!this.inputValue.trim()) return;
            
            // 创建新消息对象
            const message = {
                content: this.inputValue,
                isOutgoing: true,
                timestamp: new Date()
            };
            
            // 添加消息到数组
            this.messages.push(message);
            
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
