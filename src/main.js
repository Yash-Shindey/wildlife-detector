const { app, BrowserWindow, ipcMain } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

let mainWindow;
let pythonProcess;
let isRecording = false;

const ensureDirectories = () => {
    ['screenshots', 'recordings'].forEach(dir => {
        if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir);
        }
    });
};

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        minWidth: 1200,
        minHeight: 800,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false
        },
        backgroundColor: '#1a1a1a',
        show: false
    });

    mainWindow.loadFile(path.join(__dirname, '../public/index.html'));

    mainWindow.once('ready-to-show', () => {
        mainWindow.show();
        startDetector();
    });

    mainWindow.on('closed', () => {
        stopDetector();
        mainWindow = null;
    });
}

function startDetector() {
    try {
        if (pythonProcess) {
            stopDetector();
        }

        console.log('Starting Python detector...');
        
        pythonProcess = spawn('/opt/anaconda3/envs/wildlife-env/bin/python', [
            path.join(__dirname, 'detector.py')
        ]);
        
        let buffer = '';
        pythonProcess.stdout.on('data', (data) => {
            try {
                buffer += data.toString();
                const messages = buffer.split('\n');
                buffer = messages.pop(); // Keep incomplete message in buffer

                messages.forEach(msg => {
                    if (msg.trim()) {
                        try {
                            // Only try to parse messages that look like JSON
                            if (msg.startsWith('{')) {
                                const parsedMsg = JSON.parse(msg);
                                
                                if (parsedMsg.error) {
                                    // Log errors but don't show in UI
                                    console.error('Python error:', parsedMsg.error);
                                } else if (parsedMsg.status) {
                                    console.log('Status:', parsedMsg.status);
                                    mainWindow?.webContents.send('status', parsedMsg.status);
                                } else {
                                    mainWindow?.webContents.send('frame', msg);
                                }
                            }
                        } catch (e) {
                            // Silently ignore parse errors for YOLO debug messages
                        }
                    }
                });
            } catch (error) {
                console.error('Error processing Python output:', error);
            }
        });
        
        pythonProcess.stderr.on('data', (data) => {
            const msg = data.toString();
            // Only log errors that aren't warnings
            if (!msg.includes('ViTFeatureExtractor is deprecated')) {
                console.error('Python stderr:', msg);
            }
        });

        pythonProcess.on('error', (error) => {
            console.error('Failed to start Python process:', error);
            mainWindow?.webContents.send('error', 'Failed to start detector');
        });

        pythonProcess.on('close', (code) => {
            console.log(`Detector process exited with code ${code}`);
            if (code !== 0) {
                console.error(`Detector crashed with code ${code}`);
            }
        });

    } catch (error) {
        console.error('Failed to start detector:', error);
    }
}

function stopDetector() {
    if (pythonProcess) {
        console.log('Stopping detector...');
        pythonProcess.kill();
        pythonProcess = null;
    }
}

app.whenReady().then(() => {
    ensureDirectories();
    createWindow();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

app.on('window-all-closed', () => {
    stopDetector();
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

// IPC Handlers
ipcMain.on('switch-camera', () => {
    console.log('Switching camera...');
    if (pythonProcess?.stdin) {
        pythonProcess.stdin.write('switch_camera\n');
    }
});

ipcMain.on('capture-screenshot', () => {
    console.log('Capturing screenshot...');
    if (pythonProcess?.stdin) {
        pythonProcess.stdin.write('screenshot\n');
    }
});

ipcMain.on('toggle-recording', () => {
    isRecording = !isRecording;
    console.log(`${isRecording ? 'Starting' : 'Stopping'} recording...`);
    if (pythonProcess?.stdin) {
        pythonProcess.stdin.write('toggle_recording\n');
    }
});

ipcMain.on('quit-app', () => {
    console.log('Quitting application...');
    if (pythonProcess?.stdin) {
        pythonProcess.stdin.write('quit\n');
    }
    app.quit();
});

// Error handling
process.on('uncaughtException', (error) => {
    console.error('Uncaught exception:', error);
});

// Handle second instance
const gotTheLock = app.requestSingleInstanceLock();

if (!gotTheLock) {
    app.quit();
} else {
    app.on('second-instance', () => {
        if (mainWindow) {
            if (mainWindow.isMinimized()) {
                mainWindow.restore();
            }
            mainWindow.focus();
        }
    });
}
