"""
браузерРандомизация fingerprint模
现Canvas、WebGL、Audioи т.д.много维度Рандомизация fingerprint
"""

import random
import hashlib
import time


class FingerprintRandomizer:
    """Рандомизация fingerprint"""
    
    def __init__(self):
        # генерацияслучайный子
        self.seed = int(time.time() * 1000) % 10000
        random.seed(self.seed)
    
    def get_canvas_noise_script(self):
        """
        CanvasРандомизация fingerprintскрипт
        在Canvas渲染когдадобавить微маленький 噪，改fingerprintноне影响视觉
        """
        noise_r = random.randint(1, 10)
        noise_g = random.randint(1, 10)
        noise_b = random.randint(1, 10)
        
        script = f"""
        (function() {{
            const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
            const originalToBlob = HTMLCanvasElement.prototype.toBlob;
            const originalGetImageData = CanvasRenderingContext2D.prototype.getImageData;
            
            // добавить噪→Canvas
            const addNoise = function(canvas) {{
                const ctx = canvas.getContext('2d');
                const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
                for (let i = 0; i < imageData.data.length; i += 4) {{
                    imageData.data[i] = imageData.data[i] + {noise_r}; // R
                    imageData.data[i + 1] = imageData.data[i + 1] + {noise_g}; // G
                    imageData.data[i + 2] = imageData.data[i + 2] + {noise_b}; // B
                }}
                ctx.putImageData(imageData, 0, 0);
            }};
            
            // 覆盖toDataURL
            HTMLCanvasElement.prototype.toDataURL = function() {{
                addNoise(this);
                return originalToDataURL.apply(this, arguments);
            }};
            
            // 覆盖toBlob
            HTMLCanvasElement.prototype.toBlob = function() {{
                addNoise(this);
                return originalToBlob.apply(this, arguments);
            }};
            
            // 覆盖getImageData
            CanvasRenderingContext2D.prototype.getImageData = function() {{
                const imageData = originalGetImageData.apply(this, arguments);
                for (let i = 0; i < imageData.data.length; i += 4) {{
                    imageData.data[i] = imageData.data[i] + {noise_r};
                    imageData.data[i + 1] = imageData.data[i + 1] + {noise_g};
                    imageData.data[i + 2] = imageData.data[i + 2] + {noise_b};
                }}
                return imageData;
            }};
        }})();
        """
        return script
    
    def get_webgl_noise_script(self):
        """
        WebGLРандомизация fingerprintскрипт
        修改WebGL渲染информация и 参число
        """
        vendors = ['Intel Inc.', 'NVIDIA Corporation', 'AMD', 'Apple Inc.']
        renderers = [
            'Intel(R) UHD Graphics 620',
            'NVIDIA GeForce GTX 1660',
            'AMD Radeon RX 580',
            'Apple M1',
            'Intel(R) Iris(R) Plus Graphics'
        ]
        
        vendor = random.choice(vendors)
        renderer = random.choice(renderers)
        
        script = f"""
        (function() {{
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {{
                if (parameter === 37445) {{
                    return '{vendor}'; // UNMASKED_VENDOR_WEBGL
                }}
                if (parameter === 37446) {{
                    return '{renderer}'; // UNMASKED_RENDERER_WEBGL
                }}
                return getParameter.call(this, parameter);
            }};
            
            const getParameter2 = WebGL2RenderingContext.prototype.getParameter;
            WebGL2RenderingContext.prototype.getParameter = function(parameter) {{
                if (parameter === 37445) {{
                    return '{vendor}';
                }}
                if (parameter === 37446) {{
                    return '{renderer}';
                }}
                return getParameter2.call(this, parameter);
            }};
        }})();
        """
        return script
    
    def get_audio_noise_script(self):
        """
        AudioРандомизация fingerprintскрипт
        在AudioContextвдобавить噪
        """
        noise = random.uniform(0.00001, 0.0001)
        
        script = f"""
        (function() {{
            const audioContext = window.AudioContext || window.webkitAudioContext;
            if (audioContext) {{
                const originalCreateOscillator = audioContext.prototype.createOscillator;
                audioContext.prototype.createOscillator = function() {{
                    const oscillator = originalCreateOscillator.call(this);
                    const originalStart = oscillator.start;
                    oscillator.start = function() {{
                        // добавить微маленький 频率偏移
                        oscillator.frequency.value = oscillator.frequency.value + {noise};
                        return originalStart.apply(this, arguments);
                    }};
                    return oscillator;
                }};
            }}
        }})();
        """
        return script
    
    def get_navigator_override_script(self):
        """
        Navigatorобъект覆盖скрипт
        случайный硬并、Устройствовнутри存и т.д.информация
        """
        hardware_concurrency = random.choice([2, 4, 6, 8, 12, 16])
        device_memory = random.choice([4, 8, 16, 32])
        max_touch_points = random.choice([0, 1, 5, 10])
        
        script = f"""
        (function() {{
            // 硬并число
            Object.defineProperty(navigator, 'hardwareConcurrency', {{
                get: () => {hardware_concurrency}
            }});
            
            // Устройствовнутри存
            Object.defineProperty(navigator, 'deviceMemory', {{
                get: () => {device_memory}
            }});
            
            // 触摸число
            Object.defineProperty(navigator, 'maxTouchPoints', {{
                get: () => {max_touch_points}
            }});
            
            // 隐藏webdriverсвойство
            Object.defineProperty(navigator, 'webdriver', {{
                get: () => undefined
            }});
            
            // 插число组случайный
            const plugins = ['Chrome PDF Plugin', 'Chrome PDF Viewer', 'Native Client'];
            Object.defineProperty(navigator, 'plugins', {{
                get: () => plugins
            }});
        }})();
        """
        return script
    
    def get_screen_randomize_script(self):
        """
        屏幕информацияслучайныйскрипт
        """
        resolutions = [
            {'width': 1920, 'height': 1080},
            {'width': 1366, 'height': 768},
            {'width': 1440, 'height': 900},
            {'width': 1536, 'height': 864},
            {'width': 2560, 'height': 1440}
        ]
        
        resolution = random.choice(resolutions)
        color_depth = random.choice([24, 32])
        pixel_depth = random.choice([24, 32])
        
        script = f"""
        (function() {{
            Object.defineProperty(screen, 'width', {{
                get: () => {resolution['width']}
            }});
            
            Object.defineProperty(screen, 'height', {{
                get: () => {resolution['height']}
            }});
            
            Object.defineProperty(screen, 'availWidth', {{
                get: () => {resolution['width']}
            }});
            
            Object.defineProperty(screen, 'availHeight', {{
                get: () => {resolution['height'] - 40}
            }});
            
            Object.defineProperty(screen, 'colorDepth', {{
                get: () => {color_depth}
            }});
            
            Object.defineProperty(screen, 'pixelDepth', {{
                get: () => {pixel_depth}
            }});
        }})();
        """
        return script
    
    def get_webrtc_protect_script(self):
        """
        WebRTC IP泄露防护скрипт
        """
        script = """
        (function() {
            // 阻止WebRTC泄露TrueIP
            const originalRTCPeerConnection = window.RTCPeerConnection;
            window.RTCPeerConnection = function(config = {}) {
                // 强制использованиеПрокси，防止IP泄露
                if (!config.iceServers) {
                    config.iceServers = [];
                }
                // 禁 mDNS
                config.iceCandidatePoolSize = 0;
                return new originalRTCPeerConnection(config);
            };
        })();
        """
        return script
    
    def get_all_scripts(self):
        """
        получитьвсеРандомизация fingerprintскрипт
        """
        scripts = [
            self.get_canvas_noise_script(),
            self.get_webgl_noise_script(),
            self.get_audio_noise_script(),
            self.get_navigator_override_script(),
            self.get_screen_randomize_script(),
            self.get_webrtc_protect_script()
        ]
        
        # 合并всескрипт
        return '\n'.join(scripts)
    
    def inject_to_driver(self, driver):
        """
        将всеРандомизация fingerprintскриптинъекция→браузер
        
        Args:
            driver: Selenium WebDriver例
        """
        try:
            # 执строкавсескрипт
            combined_script = self.get_all_scripts()
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': combined_script
            })
            print("✅ Рандомизация fingerprintскриптуже инъекция")
            return True
        except Exception as e:
            print(f"⚠️  Рандомизация fingerprintинъекциянеудача: {e}")
            return False


# Глобальный инстанс
fingerprint_randomizer = FingerprintRandomizer()
