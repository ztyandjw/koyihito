export const imageConfig = {
    data() {
        return {
            showImageModal: false,
            modalImageUrl: '',
        }
    },
    methods: {
        handleImageUpload() {
            this.$refs.imageInput.click();
        },
        
        onImageSelected(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    // 添加图片消息，增加isExpanded属性
                    const message = {
                        content: e.target.result,
                        isOutgoing: true,
                        timestamp: new Date(),
                        type: 'image',
                        isExpanded: false  // 默认不展开
                    };
                    this.messages.push(message);
                    
                    // 清空文件输入框，允许重复选择同一文件
                    this.$refs.imageInput.value = '';
                    
                    // 滚动到底部
                    this.$nextTick(() => {
                        const container = document.querySelector('.messages-container');
                        this.smoothScroll(container, container.scrollHeight, 500);
                    });
                };
                reader.readAsDataURL(file);
            }
        },

        // 切换图片大小
        toggleImageSize(message) {
            message.isExpanded = !message.isExpanded;
        },

        // 点击图片时显示预览
        showOriginalImage(imageUrl) {
            this.modalImageUrl = imageUrl;
            this.showImageModal = true;
        },

        // 关闭预览
        closeImageModal() {
            this.showImageModal = false;
            this.modalImageUrl = '';
        }
    }
};
