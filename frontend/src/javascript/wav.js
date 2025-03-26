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

// 导出Vue应用配置
export const appConfig = {
    data() {
        return {
            message: '',
            isDefaultPlaceholder: true,
            inputPlaceholder: '输入你想说的内容...',
            inputValue: '',
            isMicActive: false,
            isRecording: false,
            isInputMode: true,
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
            serverURL: 'http://localhost:3888',
            useServerRecognition: true,
            isProcessing: false,
            browserSupport: browserCompatibility
        }
    },
    mounted() {
        if (!this.browserSupport.supported) {
            console.warn('浏览器不支持录音功能:', this.browserSupport.reason);
            this.inputPlaceholder = '您的浏览器不支持录音功能，请使用Chrome或Firefox';
        }
    },
    methods: {
        getMicIcon() {
            if (this.isInputMode) {
                return 'mic';
            }
            return 'keyboard';
        },
        
        getMicButtonTitle() {
            if (this.isInputMode) {
                return '切换到语音模式';
            }
            return '切换到键盘模式';
        },
        
        async handleMicClick() {
            if (this.isInputMode) {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    this.audioStream = stream;
                    this.isInputMode = false;
                    this.inputPlaceholder = '长按开始录音...';
                } catch (error) {
                    console.error('获取麦克风权限失败:', error);
                    this.inputPlaceholder = '无法访问麦克风，请检查权限设置';
                }
            } else {
                this.isInputMode = true;
                this.inputPlaceholder = '输入你想说的内容...';
                this.cleanupRecording();
            }
        },
        
        startRecording(event) {
            event.preventDefault();
            
            if (this.isInputMode || !this.audioStream || this.isRecording) {
                return;
            }
            
            try {
                this.mediaRecorder = new MediaRecorder(this.audioStream);
                this.audioChunks = [];
                
                this.mediaRecorder.ondataavailable = (event) => {
                    if (event.data.size > 0) {
                        this.audioChunks.push(event.data);
                    }
                };
                
                this.mediaRecorder.onstop = () => {
                    const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
                    this.audioBlob = audioBlob;
                    this.audioUrl = URL.createObjectURL(audioBlob);
                    this.addAudioPlayer();
                };
                
                this.mediaRecorder.start();
                this.isRecording = true;
                this.recordingStartTime = Date.now();
                this.inputPlaceholder = '正在录音...';
                
                this.updateRecordingTime();
            } catch (error) {
                console.error('开始录音失败:', error);
                this.inputPlaceholder = '录音启动失败，请重试';
            }
        },
        
        updateRecordingTime() {
            if (!this.isRecording) return;
            
            const duration = Date.now() - this.recordingStartTime;
            const seconds = Math.floor(duration / 1000);
            const milliseconds = Math.floor((duration % 1000) / 100);
            this.inputPlaceholder = `录音中: ${seconds}.${milliseconds}秒`;
            
            requestAnimationFrame(() => this.updateRecordingTime());
        },
        
        stopRecording() {
            if (!this.isRecording || !this.mediaRecorder) {
                return;
            }
            
            const duration = Date.now() - this.recordingStartTime;
            if (duration < 500) {
                this.inputPlaceholder = '录音时间太短，请重试';
                this.cleanupRecording(true);
                return;
            }
            
            try {
                this.mediaRecorder.stop();
                this.isRecording = false;
                this.inputPlaceholder = '录音已完成';
                
                setTimeout(() => {
                    const currentBlob = this.audioBlob;
                    const currentUrl = this.audioUrl;
                    
                    this.uploadAudio(currentBlob);
                    
                    this.cleanupRecording(true);
                    
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
        
        async uploadAudio(audioBlob) {
            if (!audioBlob) {
                console.error('没有可上传的音频数据');
                return;
            }
            
            try {
                console.log('开始上传音频...');
                
                const formData = new FormData();
                formData.append('audio_file', audioBlob, 'recording.wav');
                
                const response = await fetch(`${this.serverURL}/api/upload-audio`, {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) {
                    let errorMessage = `上传失败: ${response.status} ${response.statusText}`;
                    try {
                        const errorData = await response.json();
                        if (errorData && errorData.error) {
                            errorMessage = errorData.error;
                        }
                    } catch (e) {
                    }
                    throw new Error(errorMessage);
                }
                
                const result = await response.json();
                if (!result.success) {
                    throw new Error(result.error || '上传失败');
                }
                
                console.log('音频上传成功:', result);
                
            } catch (error) {
                console.error('音频上传错误:', error);
            }
        },
        
        cleanupRecording(keepStream = false) {
            this.isRecording = false;
            this.isMicActive = false;
            
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
            
            if (this.audioStream && !keepStream) {
                this.audioStream.getTracks().forEach(track => {
                    track.stop();
                    track.enabled = false;
                });
                this.audioStream = null;
            }
            
            this.audioChunks = [];
            
            this.recordingStartTime = null;
            
            if (!keepStream) {
                this.isInputMode = true;
                this.inputPlaceholder = '输入你想说的内容...';
            }
        },
        
        addAudioPlayer() {
            const existingPlayer = document.getElementById('audioPlayer');
            if (existingPlayer) {
                existingPlayer.remove();
            }
            
            const existingButton = document.getElementById('playRecordingButton');
            if (existingButton) {
                existingButton.remove();
            }
            
            const audioPlayer = document.createElement('audio');
            audioPlayer.id = 'audioPlayer';
            audioPlayer.controls = true;
            audioPlayer.style.display = 'none';
            audioPlayer.src = this.audioUrl;
            
            document.body.appendChild(audioPlayer);
            
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
            
            const icon = document.createElement('i');
            icon.className = 'material-icons';
            icon.textContent = 'play_arrow';
            icon.style.fontSize = '20px';
            playButton.prepend(icon);
            
            playButton.onmouseover = () => {
                playButton.style.backgroundColor = '#45a049';
            };
            playButton.onmouseout = () => {
                playButton.style.backgroundColor = '#4CAF50';
            };
            
            let isPlaying = false;
            
            const updatePlayState = (playing) => {
                isPlaying = playing;
                icon.textContent = playing ? 'pause' : 'play_arrow';
                playButton.title = playing ? '暂停' : '播放录音';
            };
            
            playButton.onclick = () => {
                if (isPlaying) {
                    audioPlayer.pause();
                } else {
                    audioPlayer.play();
                }
            };
            
            audioPlayer.onplay = () => updatePlayState(true);
            audioPlayer.onpause = () => updatePlayState(false);
            audioPlayer.onended = () => updatePlayState(false);
            
            const chatContainer = document.querySelector('.chat-container');
            if (chatContainer) {
                chatContainer.appendChild(playButton);
            } else {
                document.body.appendChild(playButton);
            }
        },
        
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
    unmounted() {
        this.cleanupRecording();
    }
};
