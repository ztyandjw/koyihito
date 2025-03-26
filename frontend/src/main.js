// 使用全局Vue对象
const { createApp } = Vue;

// 检查浏览器是否支持MediaRecorder
const checkBrowserCompatibility = () => {
    // 检查是否在浏览器环境中
    if (typeof window === 'undefined' || typeof navigator === 'undefined') {
        return {
            supported: false,
            reason: '不在浏览器环境中'
        };
    }
    
    // 检查MediaRecorder支持
    if (!window.MediaRecorder) {
        return {
            supported: false,
            reason: '浏览器不支持MediaRecorder API'
        };
    }
    
    // 检查getUserMedia支持
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        return {
            supported: false,
            reason: '浏览器不支持麦克风访问功能'
        };
    }
    
    return {
        supported: true,
        reason: '浏览器支持录音功能'
    };
};

// 初始化错误处理
const handleRecordingError = (error) => {
    console.error('录音错误:', error);
    if (error && error.message) {
        if (error.message.includes('Permission') || error.message.includes('permission')) {
            return '麦克风权限被拒绝，请在浏览器设置中允许访问';
        } else if (error.message.includes('device') || error.message.includes('Device')) {
            return '未检测到麦克风设备，请检查您的设备';
        } else if (error.message.includes('secure') || error.message.includes('HTTPS')) {
            return '录音功能需要安全上下文，请使用HTTPS或本地环境';
        }
    }
    return '录音初始化失败，请检查浏览器设置';
};

// 检查浏览器兼容性
const browserCompatibility = checkBrowserCompatibility();
console.log('浏览器兼容性检测结果:', browserCompatibility);

const app = createApp({
    data() {
        return {
            message: '',
            isDefaultPlaceholder: true,
            inputPlaceholder: '输入你想说的内容...',
            inputValue: '',
            isMicActive: false,
            isRecording: false,
            isInputMode: true, // 是否处于输入模式（true为输入框，false为按钮）
            audioStream: null,
            mediaRecorder: null,
            audioChunks: [],
            audioBlob: null,
            audioUrl: null,
            recordingStartTime: null,
            messages: [
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
            ],
            // 后端API相关
            serverURL: 'http://localhost:3888', // FastAPI服务器地址
            useServerRecognition: true,
            isProcessing: false,
            // 浏览器兼容性信息
            browserSupport: browserCompatibility
        }
    },
    mounted() {
        // 如果浏览器不支持录音，显示提示
        if (!this.browserSupport.supported) {
            console.warn('浏览器不支持录音功能:', this.browserSupport.reason);
            this.inputPlaceholder = '您的浏览器不支持录音功能，请使用Chrome或Firefox';
        }
    },
    methods: {
        // 获取麦克风/键盘图标
        getMicIcon() {
            if (this.isInputMode) {
                return 'mic';
            }
            return 'keyboard';
        },
        
        // 获取麦克风按钮提示文本
        getMicButtonTitle() {
            if (this.isInputMode) {
                return '切换到语音模式';
            }
            return '切换到键盘模式';
        },
        
        // 处理麦克风/键盘按钮点击
        async handleMicClick() {
            if (this.isInputMode) {
                // 从输入模式切换到语音模式
                try {
                    // 请求麦克风权限
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    this.audioStream = stream;
                    this.isInputMode = false;
                    this.inputPlaceholder = '长按开始录音...';
                } catch (error) {
                    console.error('获取麦克风权限失败:', error);
                    this.inputPlaceholder = '无法访问麦克风，请检查权限设置';
                }
            } else {
                // 从语音模式切换回输入模式
                this.isInputMode = true;
                this.inputPlaceholder = '输入你想说的内容...';
                this.cleanupRecording();
            }
        },
        
        // 开始录音（长按开始）
        startRecording(event) {
            event.preventDefault();
            
            // 只在语音模式下且未在录音时响应
            if (this.isInputMode || !this.audioStream || this.isRecording) {
                return;
            }
            
            try {
                // 创建MediaRecorder实例
                this.mediaRecorder = new MediaRecorder(this.audioStream);
                this.audioChunks = [];
                
                // 处理录音数据
                this.mediaRecorder.ondataavailable = (event) => {
                    if (event.data.size > 0) {
                        this.audioChunks.push(event.data);
                    }
                };
                
                // 录音停止时的处理
                this.mediaRecorder.onstop = () => {
                    const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
                    this.audioBlob = audioBlob;
                    this.audioUrl = URL.createObjectURL(audioBlob);
                    this.addAudioPlayer();
                };
                
                // 开始录音
                this.mediaRecorder.start();
                this.isRecording = true;
                this.recordingStartTime = Date.now();
                this.inputPlaceholder = '正在录音...';
                
                // 更新录音时间显示
                this.updateRecordingTime();
            } catch (error) {
                console.error('开始录音失败:', error);
                this.inputPlaceholder = '录音启动失败，请重试';
            }
        },
        
        // 更新录音时间显示
        updateRecordingTime() {
            if (!this.isRecording) return;
            
            const duration = Date.now() - this.recordingStartTime;
            const seconds = Math.floor(duration / 1000);
            const milliseconds = Math.floor((duration % 1000) / 100);
            this.inputPlaceholder = `录音中: ${seconds}.${milliseconds}秒`;
            
            requestAnimationFrame(() => this.updateRecordingTime());
        },
        
        // 停止录音（松开停止）
        stopRecording() {
            if (!this.isRecording || !this.mediaRecorder) {
                return;
            }
            
            const duration = Date.now() - this.recordingStartTime;
            if (duration < 500) { // 最短录音时间500ms
                this.inputPlaceholder = '录音时间太短，请重试';
                this.cleanupRecording(true);
                return;
            }
            
            try {
                this.mediaRecorder.stop();
                this.isRecording = false;
                this.inputPlaceholder = '录音已完成';
                
                // 在录音完成后延迟清理资源，确保数据被保存
                setTimeout(() => {
                    // 保存当前的 audioBlob 和 audioUrl，因为它们还需要用于播放
                    const currentBlob = this.audioBlob;
                    const currentUrl = this.audioUrl;
                    
                    // 上传音频到后端
                    this.uploadAudio(currentBlob);
                    
                    // 清理除了播放需要的资源外的所有内容
                    this.cleanupRecording(true);
                    
                    // 恢复需要的播放资源
                    this.audioBlob = currentBlob;
                    this.audioUrl = currentUrl;
                }, 100);
                
                setTimeout(() => {
                    this.inputPlaceholder = '长按开始录音...';
                }, 1000);
            } catch (error) {
                console.error('停止录音失败:', error);
                this.cleanupRecording(true);
            }
        },
        
        // 上传音频到后端
        async uploadAudio(audioBlob) {
            if (!audioBlob) {
                console.error('没有可上传的音频数据');
                return;
            }
            
            try {
                console.log('开始上传音频...');
                
                // 创建FormData对象
                const formData = new FormData();
                formData.append('audio_file', audioBlob, 'recording.wav');
                
                // 发送到后端
                const response = await fetch(`${this.serverURL}/api/upload-audio`, {
                    method: 'POST',
                    body: formData
                });
                
                // 检查响应状态
                if (!response.ok) {
                    let errorMessage = `上传失败: ${response.status} ${response.statusText}`;
                    try {
                        const errorData = await response.json();
                        if (errorData && errorData.error) {
                            errorMessage = errorData.error;
                        }
                    } catch (e) {
                        // 解析错误响应失败，使用默认错误消息
                    }
                    throw new Error(errorMessage);
                }
                
                // 解析响应
                const result = await response.json();
                if (!result.success) {
                    throw new Error(result.error || '上传失败');
                }
                
                console.log('音频上传成功:', result);
                
            } catch (error) {
                console.error('音频上传错误:', error);
            }
        },
        
        // 清理录音资源
        cleanupRecording(keepStream = false) {
            // 重置所有状态
            this.isRecording = false;
            this.isMicActive = false;
            
            // 停止并清理 MediaRecorder
            if (this.mediaRecorder) {
                try {
                    if (this.mediaRecorder.state !== 'inactive') {
                        this.mediaRecorder.stop();
                    }
                } catch (e) {
                    console.error('停止MediaRecorder失败:', e);
                }
                this.mediaRecorder = null;
            }
            
            // 停止并清理音频流（除非指定保留）
            if (this.audioStream && !keepStream) {
                this.audioStream.getTracks().forEach(track => {
                    track.stop();
                    track.enabled = false;
                });
                this.audioStream = null;
            }
            
            // 清理音频数据
            this.audioChunks = [];
            
            // 重置录音时间
            this.recordingStartTime = null;
            
            // 如果不保留流，则重置为输入模式
            if (!keepStream) {
                this.isInputMode = true;
                this.inputPlaceholder = '输入你想说的内容...';
            }
        },
        
        // 添加音频播放器
        addAudioPlayer() {
            // 移除现有播放器
            const existingPlayer = document.getElementById('audioPlayer');
            if (existingPlayer) {
                existingPlayer.remove();
            }
            
            const existingButton = document.getElementById('playRecordingButton');
            if (existingButton) {
                existingButton.remove();
            }
            
            // 创建新的音频播放器
            const audioPlayer = document.createElement('audio');
            audioPlayer.id = 'audioPlayer';
            audioPlayer.controls = true;
            audioPlayer.style.display = 'none';
            audioPlayer.src = this.audioUrl;
            
            // 添加到body
            document.body.appendChild(audioPlayer);
            
            // 创建播放按钮
            const playButton = document.createElement('button');
            playButton.textContent = '播放录音';
            playButton.id = 'playRecordingButton';
            playButton.style.position = 'fixed';
            playButton.style.bottom = '60px';
            playButton.style.right = '20px';
            playButton.style.zIndex = '1000';
            playButton.style.padding = '8px 16px';
            playButton.style.backgroundColor = '#4CAF50';
            playButton.style.color = 'white';
            playButton.style.border = 'none';
            playButton.style.borderRadius = '20px';
            playButton.style.cursor = 'pointer';
            playButton.style.boxShadow = '0 2px 5px rgba(0,0,0,0.2)';
            playButton.style.display = 'flex';
            playButton.style.alignItems = 'center';
            playButton.style.gap = '5px';
            
            // 添加图标
            const icon = document.createElement('i');
            icon.className = 'material-icons';
            icon.textContent = 'play_arrow';
            icon.style.fontSize = '20px';
            playButton.prepend(icon);
            
            // 添加悬停效果
            playButton.onmouseover = () => {
                playButton.style.backgroundColor = '#45a049';
            };
            playButton.onmouseout = () => {
                playButton.style.backgroundColor = '#4CAF50';
            };
            
            // 播放状态管理
            let isPlaying = false;
            
            // 更新播放状态
            const updatePlayState = (playing) => {
                isPlaying = playing;
                icon.textContent = playing ? 'pause' : 'play_arrow';
                playButton.title = playing ? '暂停' : '播放录音';
            };
            
            // 点击事件处理
            playButton.onclick = () => {
                if (isPlaying) {
                    audioPlayer.pause();
                } else {
                    audioPlayer.play();
                }
            };
            
            // 监听音频播放状态
            audioPlayer.onplay = () => updatePlayState(true);
            audioPlayer.onpause = () => updatePlayState(false);
            audioPlayer.onended = () => updatePlayState(false);
            
            // 添加到chat-container
            const chatContainer = document.querySelector('.chat-container');
            if (chatContainer) {
                chatContainer.appendChild(playButton);
            } else {
                document.body.appendChild(playButton);
            }
        },
        
        // 发送消息方法
        sendMessage() {
            if (!this.inputValue.trim()) return;
            
            const message = {
                content: this.inputValue,
                isOutgoing: true,
                timestamp: new Date()
            };
            
            this.messages.push(message);
            this.inputValue = '';
            this.inputPlaceholder = '输入你想说的内容...';
            
            this.$nextTick(() => {
                const messagesContainer = document.querySelector('.messages-container');
                if (messagesContainer) {
                    messagesContainer.scrollTop = messagesContainer.scrollHeight;
                }
            });
        }
    },
    
    // 组件销毁时清理资源
    unmounted() {
        this.cleanupRecording();
    }
})

app.mount('#app')
