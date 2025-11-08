// 后端 Flask 应用的地址和端口
const API_URL = 'http://127.0.0.1:5000'; 

// --- 获取 DOM 元素 ---
const loginForm = document.getElementById('login-form');
const loginContainer = document.getElementById('login-container');
const loginMessage = document.getElementById('login-message');

const infoStudentMessage = document.getElementById('info-student-message');
const infoTutorMessage = document.getElementById('info-tutor-message');
const infoWardenMessage = document.getElementById('info-warden-message');

const studentDashboard = document.getElementById('student-dashboard');  // 学生仪表盘
const tutorDashboard = document.getElementById('tutor-dashboard');  // 导师仪表盘
const wardenDashboard = document.getElementById('warden-dashboard');  // 舍监仪表盘

const newStudentPhoneInput = document.getElementById('new-phone-input');
const newTutorPhoneInput = document.getElementById('new-tutor-phone-input');
const newWardenPhoneInput = document.getElementById('new-warden-phone-input');

// 处理学生宿舍信息及电费余额
const dormMessage = document.getElementById('dorm-message');
const balanceEl = document.getElementById('info-electricity-balance');
const amountInput = document.getElementById('recharge-amount');
const rechargeMsg = document.getElementById('recharge-message');
const rechargeBtn = document.getElementById('recharge-btn');

// 所有仪表盘容器
const dashboards = {
    'student': studentDashboard,
    'tutor': tutorDashboard,
    'warden': wardenDashboard
};

const phoneEditElements = {
    'student': {
        editBtn: document.getElementById('student-edit-btn'),    // 假设学生修改按钮ID为 student-edit-btn
        updateForm: document.getElementById('student-update-form'), // 假设学生表单ID为 student-update-form
        input: newStudentPhoneInput,
    },
    'tutor': {
        editBtn: document.getElementById('tutor-edit-btn'),
        updateForm: document.getElementById('tutor-update-form'),
        input: newTutorPhoneInput,
    },
    'warden': {
        editBtn: document.getElementById('warden-edit-btn'),
        updateForm: document.getElementById('warden-update-form'),
        input: newWardenPhoneInput,
    }
};


// --- 辅助函数：显示/隐藏仪表盘 ---
function showDashboard(role, userInfo) {
    // 隐藏所有内容
    loginContainer.classList.add('hidden');
    Object.values(dashboards).forEach(d => d.classList.add('hidden'));

    // 显示对应的仪表盘
    const dashboard = dashboards[role];
    if (dashboard) {
        dashboard.classList.remove('hidden');

        let nameElement, name;
        
        if (role === 'student') {
            nameElement = document.getElementById('student-name');
            name = userInfo.STUDENT_NAME || localStorage.getItem('user_id'); 
            setupDashboardNavigation(dashboard, 'student-info-tab');    // 打开 'student-info-tab'
            loadStudentInfo(localStorage.getItem('user_id'));

        } else if (role === 'tutor') {
            nameElement = document.getElementById('tutor-name');
            name = userInfo.TUTOR_NAME || localStorage.getItem('user_id');
            setupDashboardNavigation(dashboard, 'tutor-info-tab');    // 打开 'tutor-info-tab'
            loadTutorInfo(localStorage.getItem('user_id'));

        } else if (role === 'warden') {
            nameElement = document.getElementById('warden-name');
            name = userInfo.WARDEN_NAME || localStorage.getItem('user_id');
            setupDashboardNavigation(dashboard, 'warden-info-tab');    // 打开 'warden-info-tab'
            loadWardenInfo(localStorage.getItem('user_id'));
        }
        
        if (nameElement) {
            nameElement.textContent = name;
        }
        
    } else {
        console.error('未知的用户角色:', role);
        loginMessage.textContent = 'Login successful, but information unknown.';
        logout(); // 角色未知则退出登录
    }
}

// 辅助函数
function setupDashboardNavigation(dashboard, defaultTabId) {
    const navButtons = dashboard.querySelectorAll('.nav-btn');
    const tabContents = dashboard.querySelectorAll('.tab-content');

    // 显示指定的默认 Tab
    const defaultTab = document.getElementById(defaultTabId);
    if (defaultTab) {
        tabContents.forEach(tab => tab.classList.add('hidden'));
        defaultTab.classList.remove('hidden');
        defaultTab.classList.add('current-tab');

        navButtons.forEach(btn => {
            if (btn.dataset.target === defaultTabId) btn.classList.add('current');
            else btn.classList.remove('current');
        });
    }

    // 点击按钮切换 Tab，并在必要时触发数据加载
    navButtons.forEach(button => {
        button.addEventListener('click', (event) => {
            const targetId = event.currentTarget.dataset.target;

            // 切换 Tab 显示
            tabContents.forEach(tab => {
                tab.classList.add('hidden');
                tab.classList.remove('current-tab');
            });
            const targetTab = document.getElementById(targetId);
            if (targetTab) {
                targetTab.classList.remove('hidden');
                targetTab.classList.add('current-tab');
            }

            // 更新按钮样式
            navButtons.forEach(btn => btn.classList.remove('current'));
            event.currentTarget.classList.add('current');

            // 根据 role 与目标 tab 调用相应的加载器
            const role = localStorage.getItem('role');
            const userId = localStorage.getItem('user_id');

            // 如果切换到个人信息页，加载相应信息（学生/导师/舍监）
            if (targetId === 'student-info-tab' && role === 'student') {loadStudentInfo(userId);}
            if (targetId === 'tutor-info-tab' && role === 'tutor') {loadTutorInfo(userId);}
            if (targetId === 'warden-info-tab' && role === 'warden') {loadWardenInfo(userId);}

            if (targetId === 'student-dorm-tab' && role === 'student') {loadStudentDormInfo(userId);}
            if (targetId === 'student-repair-tab' && role === 'student') {loadStudentRoom(userId);}
            if (targetId === 'student-adjust-tab' && role === 'student') {loadStudentAdjust(userId);}
            if (targetId === 'tutor-student-tab' && role === 'tutor') {loadTutorStudentInfo(userId);}
            if (targetId === 'tutor-repair-tab' && role === 'tutor') {loadTutorRepairRequests(userId);}
            if (targetId === 'warden-tutor-tab' && role === 'warden') {loadWardenTutorInfo(userId);}
            if (targetId === 'warden-student-tab' && role === 'warden') {loadWardenStudentInfo(userId);}
            if (targetId === 'warden-dorm-tab' && role === 'warden') {loadWardenDormInfo(userId);}
            if (targetId === 'warden-adjust-tab' && role === 'warden') {loadWardenAdjustRequests(userId);}
        });
    });
}

// 处理登录表单提交
async function handleLogin(event) {
    event.preventDefault(); 

    const userId = document.getElementById('user-id').value;
    const password = document.getElementById('password').value;

    loginMessage.textContent = ''; 
    loginMessage.style.color = 'red';

    const loginBtn = document.querySelector('.login-btn');
    loginBtn.disabled = true;
    loginBtn.textContent = 'Logging in...';

    try {
        const response = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: userId, password: password }),
        });

        const data = await response.json(); 

        if (response.ok && data.success) {
            loginMessage.textContent = 'Login successful! Redirecting...';
            loginMessage.style.color = 'green';
            
            // 存储必要的用户信息
            localStorage.setItem('role', data.role);
            localStorage.setItem('user_id', userId);
            localStorage.setItem('user_info', JSON.stringify(data.user_info));
            
            showDashboard(data.role, data.user_info);

        } else {
            const message = data.message || 'Login failed, please check your ID and password.';
            loginMessage.textContent = message;
        }
        
    } catch (error) {
        console.error('网络或服务器连接错误:', error);
        loginMessage.textContent = 'Cannot connect to server, please check backend at ' + API_URL;
    } finally {
        loginBtn.disabled = false;
        loginBtn.textContent = 'Login Now';
    }
}

// --- 学生信息模块 ---

/**
 * 加载并显示学生的个人信息。
 * @param {string} studentId - 学生 ID
 */
async function loadStudentInfo(studentId) {
    // 确保我们当前在个人信息 Tab 
    if (!document.getElementById('student-info-tab').classList.contains('current-tab')) {
        return; // 如果不在当前 Tab，则不加载，避免不必要的请求
    }
    
    // 重置手机号编辑状态
    toggleEditPhone(false);

    infoStudentMessage.textContent = 'Loading student info...';
    infoStudentMessage.style.color = 'gray';
    
    try {
        const response = await fetch(`${API_URL}/student/info?id=${studentId}`);
        const data = await response.json();

        // 在控制台打印后端返回的原始数据
        console.log('--- 后端 /student/info 原始返回数据 ---');
        console.log(data);
        
        if (response.ok && data.success) {
            const info = data.info;
            
            // 调试：打印提取的 info 对象
            console.log('--- 提取的 info 对象 ---');
            console.log(info);

            // 填充信息到 HTML 元素中
            document.getElementById('info-id').textContent = info.STUDENT_ID || 'N/A';
            document.getElementById('info-name').textContent = info.STUDENT_NAME || 'N/A';
            document.getElementById('info-gender').textContent = info.GENDER || 'N/A';
            document.getElementById('info-school').textContent = info.SCHOOL || 'N/A';
            document.getElementById('info-major').textContent = info.MAJOR || 'N/A';            
            document.getElementById('info-dormroom').textContent = info.ROOM_ID || 'N/A'; 
            document.getElementById('info-phone').textContent = info.STUDENT_PHONE_NUM || 'N/A';
            document.getElementById('info-email').textContent = info.STUDENT_EMAIL_ADDRESS || 'N/A';
            infoStudentMessage.textContent = 'Info loaded successfully.';
            infoStudentMessage.style.color = 'green';
        } else {
            infoStudentMessage.textContent = data.message || 'Failed to load info.';
            infoStudentMessage.style.color = 'red';
        }
    } catch (error) {
        console.error('加载学生信息时发生网络错误或JSON解析错误:', error);
        infoStudentMessage.textContent = 'Network error, cannot fetch student info.';
        infoStudentMessage.style.color = 'red';
    }
}

async function loadStudentDormInfo(studentId) {
    // 只在该 Tab 为当前显示时请求，避免不必要请求
    if (!document.getElementById('student-dorm-tab').classList.contains('current-tab')) {
        return;
    }

    dormMessage.textContent = 'Loading dorm info...';
    dormMessage.style.color = 'gray';

    try {
        const res = await fetch(`${API_URL}/student/dorm_info?id=${encodeURIComponent(studentId)}`);
        const data = await res.json();

        console.log('后端 /student/dorm_info 返回：', data);

        if (res.ok && data.success) {
            const info = data.dorm_info || {};

            document.getElementById('info-building-id').textContent = info.BUILDING_ID || 'N/A';
            document.getElementById('info-floor-id').textContent = info.FLOOR_ID || 'N/A';
            document.getElementById('info-room-id').textContent = info.ROOM_ID || 'N/A';
            document.getElementById('info-bed-id').textContent = info.BED_ID || 'N/A';
            document.getElementById('info-reqtbp-id').textContent = info.REQ_TBPROCESSED_NUM || '0';
            document.getElementById('info-reqhbp-id').textContent = info.REQ_HBPROCESSED_NUM || '0';

            // 电费余额可能为数字或字符串，格式化显示
            const balance = info.ELECTRICITY_BALANCE ?? info.balance ?? null;
            balanceEl.textContent = (balance !== null && balance !== undefined) ? Number(balance).toFixed(2) : '0.00';
            balanceEl.style.color = Number(balance) < 0 ? 'red' : Number(balance) > 0 ? 'green' : 'black';
            
            dormMessage.textContent = 'Drom info loaded successfully.';
            dormMessage.style.color = 'green';
        } else {
            dormMessage.textContent = data.message || 'Unable to fetch dorm information';
            dormMessage.style.color = 'red';
            balanceEl.textContent = '0.00';
        }
    } catch (err) {
        console.error('获取宿舍信息出错：', err);
        dormMessage.textContent = 'Network error, cannot fetch dorm info.';
        dormMessage.style.color = 'red';
        balanceEl.textContent = '0.00';
    }
}

/**
 * 处理充值请求，调用后端 /student/recharge_electricity
 * 并在成功后更新页面显示的余额
 * @param {Event} event
 */
async function handleRecharge(event) {
    event.preventDefault();

    const userId = localStorage.getItem('user_id');

    // 基本校验
    const raw = amountInput.value;
    const amount = raw ? Number(raw) : 0;
    if (!userId) {
        rechargeMsg.textContent = 'No user found. Please log in again.';
        rechargeMsg.style.color = 'red';
        return;
    }
    if (!amount || isNaN(amount) || amount <= 0) {
        rechargeMsg.textContent = 'Please enter a valid amount (greater than 10, step 1).';
        rechargeMsg.style.color = 'red';
        return;
    }

    rechargeBtn.disabled = true;
    rechargeBtn.textContent = 'Recharging...';
    rechargeMsg.textContent = 'Submitting recharge request...';
    rechargeMsg.style.color = 'gray';

    try {
        const res = await fetch(`${API_URL}/student/recharge_electricity`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: userId, amount: amount })
        });
        const data = await res.json();
        console.log('后端 /student/recharge_electricity 返回：', data);

        if (res.ok && data.success) {
            // 如果后端返回 new_balance，优先使用；否则重新请求 dorm_info 刷新
            if (data.new_balance !== undefined && data.new_balance !== null && !isNaN(Number(data.new_balance))) {
                balanceEl.textContent = Number(data.new_balance).toFixed(2);
            } else {
                // 后端没有返回具体余额时，重新调用 dorm_info 更新
                await loadStudentDormInfo(userId);
            }

            rechargeMsg.textContent = data.message || `Recharge successful: ${amount.toFixed(2)} yuan.`;
            rechargeMsg.style.color = 'green';
            amountInput.value = ''; // 清空输入框
        } else {
            rechargeMsg.textContent = data.message || 'Recharge failed, please try again later.';
            rechargeMsg.style.color = 'red';
        }
    } catch (err) {
        console.error('充值请求出错：', err);
        rechargeMsg.textContent = 'Network error, recharge failed.';
        rechargeMsg.style.color = 'red';
    } finally {
        rechargeBtn.disabled = false;
        rechargeBtn.textContent = 'Recharge';
    }
}

async function loadStudentRoom(studentId) {
    const selectEl = document.getElementById('repair-room');
    selectEl.innerHTML = '<option value="" disabled selected>Loading...</option>';

    try {
        const response = await fetch(`${API_URL}/student/rooms?id=${studentId}`);
        const data = await response.json();

        if (response.ok && data.success && data.rooms.length > 0) {
            selectEl.innerHTML = '';
            const room = data.rooms[0]; // 取自己的宿舍号
            const option = document.createElement('option');
            option.value = room.ROOM_ID;
            option.textContent = room.ROOM_ID;
            selectEl.appendChild(option);
        } else {
            selectEl.innerHTML = '<option value="" disabled>Unable to find dorm ID</option>';
        }
    } catch (error) {
        console.error('加载学生宿舍号失败:', error);
        selectEl.innerHTML = '<option value="" disabled>Loading failed</option>';
    }
}

async function loadStudentAdjust(studentId) {
    const buildingEl = document.getElementById('adjust-building');
    const floorEl = document.getElementById('adjust-floor');
    const roomEl = document.getElementById('adjust-room');
    const bedEl = document.getElementById('adjust-bed');

    buildingEl.innerHTML = '<option value="" disabled selected>Loading...</option>';
    floorEl.innerHTML = '<option value="" disabled selected>Select floor</option>';
    roomEl.innerHTML = '<option value="" disabled selected>Select room</option>';
    bedEl.innerHTML = '<option value="" disabled selected>Select bed</option>';

    try {
        // 获取学生信息（含性别）
        const studentRes = await fetch(`${API_URL}/student/info?id=${studentId}`);
        const studentData = await studentRes.json();
        if (!studentData.success) throw 'Unable to fetch student info.';
        const gender = studentData.info.GENDER;

        // 加载自己的楼栋（只有一个可选）
        const buildingRes = await fetch(`${API_URL}/student/buildings?id=${studentId}`);
        const buildingData = await buildingRes.json();
        if (buildingRes.ok && buildingData.success && buildingData.buildings.length > 0){
            buildingEl.innerHTML = '';
            const building = buildingData.buildings[0];
            const option = document.createElement('option');
            option.value = building.BUILDING_ID;
            option.textContent = building.BUILDING_ID;
            buildingEl.appendChild(option);
        }else{
            buildingEl.innerHTML = '<option value="" disabled>Unable to find building</option>';
        }
            
        // 根据性别限制楼层
        const floors = (gender === '女') ? [3,5,7] : [2,4,6,8];
        floorEl.innerHTML = '<option value="" disabled selected>Select floor</option>';
        floors.forEach(f => {
            const opt = document.createElement('option');
            opt.value = f;
            opt.textContent = f;
            floorEl.appendChild(opt);
        });

        // 选择楼层 -> 加载可用房间
        floorEl.addEventListener('change', async () => {
            roomEl.innerHTML = '<option value="" disabled selected>Loading...</option>';
            bedEl.innerHTML = '<option value="" disabled selected>Select bed</option>';

            console.log("信息：", buildingEl.value, floorEl.value)
            const res = await fetch(`${API_URL}/student/adjust/rooms?building_id=${buildingEl.value}&floor_id=${floorEl.value}`);
            const data = await res.json();
            if (data.success && data.rooms.length > 0) {
                roomEl.innerHTML = '<option value="" disabled selected>Select room</option>';
                data.rooms.forEach(r => {
                    const opt = document.createElement('option');
                    opt.value = r.ROOM_ID;
                    opt.textContent = r.ROOM_ID;
                    roomEl.appendChild(opt);
                });
            } else {
                roomEl.innerHTML = '<option value="" disabled>No available room</option>';
            }
        });

        // 选择房间 -> 加载可用床位
        roomEl.addEventListener('change', async () => {
            const selectedRoom = roomEl.value;
            bedEl.innerHTML = '<option value="" disabled selected>Loading...</option>';

            const res = await fetch(`${API_URL}/student/adjust/beds?room_id=${selectedRoom}`);
            const data = await res.json();
            if (data.success && data.beds.length > 0) {
                bedEl.innerHTML = '<option value="" disabled selected>Select bed</option>';
                data.beds.forEach(b => {
                    const opt = document.createElement('option');
                    opt.value = b.BED_ID;
                    opt.textContent = b.BED_ID;
                    bedEl.appendChild(opt);
                });
            } else {
                bedEl.innerHTML = '<option value="" disabled>No available bed</option>';
            }
        });

    } catch (err) {
        console.error('加载宿舍调整表单失败', err);
        buildingEl.innerHTML = '<option value="" disabled>Loading failed</option>';
    }
}


// --- 导师信息模块 ---

/**
 * 加载并显示导师的个人信息。
 * @param {string} tutorId - 导师 ID
 */
async function loadTutorInfo(tutorId) {
    // 确保我们当前在个人信息 Tab 
    if (!document.getElementById('tutor-info-tab').classList.contains('current-tab')) {
        return; // 如果不在当前 Tab，则不加载，避免不必要的请求
    }
    
    // 重置手机号编辑状态
    toggleEditPhone(false);

    infoTutorMessage.textContent = 'Loading info...';
    infoTutorMessage.style.color = 'gray';
    
    try {
        const response = await fetch(`${API_URL}/tutor/info?id=${tutorId}`);
        const data = await response.json();

        // 在控制台打印后端返回的原始数据
        console.log('--- 后端 /tutor/info 原始返回数据 ---');
        console.log(data);
        
        if (response.ok && data.success) {
            const info = data.info;
            
            // 调试：打印提取的 info 对象
            console.log('--- 提取的 info 对象 ---');
            console.log(info);

            // 填充信息到 HTML 元素中
            document.getElementById('info-tutor-id').textContent = info.TUTOR_ID || 'N/A';
            document.getElementById('info-tutor-name').textContent = info.TUTOR_NAME || 'N/A';
            document.getElementById('info-tutor-gender').textContent = info.TUTOR_GENDER || 'N/A';  
            document.getElementById('info-tutor-email').textContent = info.TUTOR_EMAIL_ADDRESS || 'N/A';
            document.getElementById('info-tutor-phone').textContent = info.TUTOR_PHONE_NUM || 'N/A';
            infoTutorMessage.textContent = 'Info loaded successfully.';
            infoTutorMessage.style.color = 'green';
        } else {
            infoTutorMessage.textContent = data.message || 'Failed to load info.';
            infoTutorMessage.style.color = 'red';
        }
    } catch (error) {
        console.error('加载导师信息时发生网络错误或JSON解析错误:', error);
        infoTutorMessage.textContent = 'Network error, cannot fetch tutor info.';
        infoTutorMessage.style.color = 'red';
    }
}

async function loadTutorStudentInfo(tutorId) {
    if (!document.getElementById('tutor-student-tab').classList.contains('current-tab')) {
        return; // 如果不在当前 Tab，则不加载，避免不必要的请求
    }
    const messageTS = document.getElementById('tutor-student-message');
    const listEl = document.getElementById('tutor-student-table-body');
    messageTS.textContent = 'Loading student info';
    messageTS.style.color = 'gray';
    listEl.innerHTML = ''; // 清空列表
    
    try {
        const response = await fetch(`${API_URL}/tutor/students?id=${tutorId}`);
        const data = await response.json();

        // 在控制台打印后端返回的原始数据
        console.log('--- 后端 /tutor/students 原始返回数据 ---');
        console.log(data);
        
        if (response.ok && data.success) {
            messageTS.textContent = `Students of ${data.floor_id} foor information loaded successfully.`;
            messageTS.style.color = 'green';
            if (data.students && data.students.length > 0) {
                data.students.forEach(student => {
                    const row = `
                        <tr>
                            <td>${student.STUDENT_ID}</td>
                            <td>${student.STUDENT_NAME}</td>
                            <td>${student.GENDER}</td>
                            <td>${student.SCHOOL}</td>
                            <td>${student.MAJOR}</td>
                            <td>${student.STUDENT_PHONE_NUM}</td>
                            <td>${student.ROOM_ID}</td>
                            <td>${student.BED_ID}</td>
                            </td>
                        </tr>
                    `;
                    listEl.insertAdjacentHTML('beforeend', row);
                });
            }else {
                listEl.innerHTML = '<tr><td colspan="8" class="text-center py-4">No students found in the building.</td></tr>';
            }
        } else {
            messageTS.textContent = data.message || 'Failed to fetch student info';
            messageTS.style.color = 'red';
        }
    } catch (error) {
        console.error('获取学生信息时发生网络错误:', error);
        messageTS.textContent = 'Network error, cannot load student info.';
        messageTS.style.color = 'red';
    }
}

async function loadTutorRepairRequests(tutorId) {
    const tbody = document.getElementById('repair-table-body');
    tbody.innerHTML = '<tr><td colspan="4" class="text-center">Loading...</td></tr>';
    
    const reqHBProcessed = document.getElementById('summary-req-hbprocessed');
    const reqTBProcessed = document.getElementById('summary-req-tbprocessed');
    
    try {
        const res = await fetch(`${API_URL}/tutor/pending_requests?id=${tutorId}`);
        const data = await res.json();
        const info = data.requests || {};
        reqHBProcessed.textContent = info.TUTOR_HBPROCESSED_REQ_NUM ?? '0';
        reqTBProcessed.textContent = info.TUTOR_TBPROCESSED_REQ_NUM ?? '0';
        
        if (res.ok && data.success && data.students.length > 0) {
            tbody.innerHTML = '';
            data.students.forEach(student => {
                const tr = document.createElement('tr');

                tr.innerHTML = `
                    <td>${student.STUDENT_ID}</td>
                    <td>${student.STUDENT_NAME}</td>
                    <td>${student.ROOM_ID}</td>
                    <td>${student.REPAIR_TYPE}</td>
                    <td>
                        <button class="btn-action btn-approve" data-request="${student.REQUEST_ID}" data-room="${student.ROOM_ID}" data-action="Approve">Approve</button>
                        <button class="btn-action btn-reject" data-request="${student.REQUEST_ID}" data-room="${student.ROOM_ID}" data-action="Reject">Reject</button>
                    </td>
                `;
                tbody.appendChild(tr);
            });

            // 添加按钮点击事件
            tbody.querySelectorAll('.btn-action').forEach(btn => {
                btn.addEventListener('click', async () => {
                    const roomId = btn.dataset.room;
                    const requestId = btn.dataset.request;
                    const action = btn.dataset.action;
                    btn.disabled = true;

                    try {
                        const res = await fetch(`${API_URL}/tutor/process_repair_request?id=${tutorId}`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ request_id: requestId, room_id: roomId, action: action})
                        });
                        const result = await res.json();
                        alert(result.message);
                        if (result.success) {
                            // 操作成功后刷新表格
                            await loadTutorRepairRequests(tutorId);
                        } else {
                            btn.disabled = false;
                        }
                    } catch (err) {
                        console.error('处理维修请求失败:', err);
                        alert('Network error. Failed to process request.');
                        btn.disabled = false;
                    }
                });
            });
        } else {
            tbody.innerHTML = '<tr><td colspan="5" class="req-empty-table text-center">No pending requests</td></tr>';
        }
    } catch (err) {
        console.error('加载维修请求失败:', err);
        tbody.innerHTML = '<tr><td colspan="4" class="req-empty-table text-center">Loading failed</td></tr>';
    }
}

// --- 舍监信息模块 ---

/**
 * 加载并显示舍监的个人信息。
 * @param {string} wardenId - 舍监 ID
 */
async function loadWardenInfo(wardenId) {
    // 确保我们当前在个人信息 Tab 
    if (!document.getElementById('warden-info-tab').classList.contains('current-tab')) {
        return; // 如果不在当前 Tab，则不加载，避免不必要的请求
    }
    
    // 重置手机号编辑状态
    toggleEditPhone(false);

    infoWardenMessage.textContent = 'Loading info...';
    infoWardenMessage.style.color = 'gray';
    
    try {
        const response = await fetch(`${API_URL}/warden/info?id=${wardenId}`);
        const data = await response.json();

        // 在控制台打印后端返回的原始数据
        console.log('--- 后端 /warden/info 原始返回数据 ---');
        console.log(data);
        
        if (response.ok && data.success) {
            const info = data.info;
            
            // 调试：打印提取的 info 对象
            console.log('--- 提取的 info 对象 ---');
            console.log(info);

            // 填充信息到 HTML 元素中
            document.getElementById('info-warden-id').textContent = info.WARDEN_ID || 'N/A';
            document.getElementById('info-warden-name').textContent = info.WARDEN_NAME || 'N/A';
            document.getElementById('info-warden-gender').textContent = info.WARDEN_GENDER || 'N/A';  
            document.getElementById('info-warden-email').textContent = info.WARDEN_EMAIL_ADDRESS || 'N/A';
            document.getElementById('info-warden-phone').textContent = info.WARDEN_PHONE_NUM || 'N/A';
            infoWardenMessage.textContent = 'Info loaded successfully.';
            infoWardenMessage.style.color = 'green';
        } else {
            infoWardenMessage.textContent = data.message || 'Failed to load info.';
            infoWardenMessage.style.color = 'red';
        }
    } catch (error) {
        console.error('加载舍监信息时发生网络错误或JSON解析错误:', error);
        infoWardenMessage.textContent = 'Network error, cannot fetch warden info.';
        infoWardenMessage.style.color = 'red';
    }
}

async function loadWardenTutorInfo(wardenId) {
    if (!document.getElementById('warden-tutor-tab').classList.contains('current-tab')) {
        return; // 如果不在当前 Tab，则不加载，避免不必要的请求
    }
    const messageWT = document.getElementById('warden-tutor-message');
    const listEl = document.getElementById('warden-tutor-table-body');
    messageWT.textContent = 'Loading tutor info...';
    messageWT.style.color = 'gray';
    listEl.innerHTML = ''; // 清空列表
    
    try {
        const response = await fetch(`${API_URL}/warden/tutors?id=${wardenId}`);
        const data = await response.json();

        // 在控制台打印后端返回的原始数据
        console.log('--- 后端 /warden/tutors 原始返回数据 ---');
        console.log(data);
        
        if (response.ok && data.success) {
            messageWT.textContent = `Tutors of ${data.building_id} building information loaded successfully.`;
            messageWT.style.color = 'green';
            if (data.tutors && data.tutors.length > 0) {
                data.tutors.forEach(tutor => {
                    const row = `
                        <tr class="hover:bg-gray-100">
                            <td>${tutor.TUTOR_ID}</td>
                            <td>${tutor.TUTOR_NAME}</td>
                            <td>${tutor.TUTOR_GENDER}</td>
                            <td>${tutor.TUTOR_PHONE_NUM}</td>
                            <td>${tutor.FLOOR_ID || '无'}</td>
                            <td class="px-3 py-2 whitespace-nowrap text-center font-bold ${tutor.TUTOR_TBPROCESSED_REQ_NUM > 0 ? 'text-red-600' : 'text-green-600'}">
                                ${tutor.TUTOR_TBPROCESSED_REQ_NUM || 0}
                            </td>
                        </tr>
                    `;
                    listEl.insertAdjacentHTML('beforeend', row);
                });
            }else {
                listEl.innerHTML = '<tr><td colspan="6" class="text-center py-4">No tutors found in this building.</td></tr>';
            }
        } else {
            messageWT.textContent = data.message || 'Failed to fetch tutor info.';
            messageWT.style.color = 'red';
        }
    } catch (error) {
        console.error('获取导师信息时发生网络错误:', error);
        messageWT.textContent = 'Network error, cannot load tutor info.';
        messageWT.style.color = 'red';
    }
}

async function loadWardenStudentInfo(wardenId) {
    if (!document.getElementById('warden-student-tab').classList.contains('current-tab')) {
        return; // 如果不在当前 Tab，则不加载，避免不必要的请求
    }
    const messageWS = document.getElementById('warden-student-message');
    const listEl = document.getElementById('warden-student-table-body');
    messageWS.textContent = 'Loading student info';
    messageWS.style.color = 'gray';
    listEl.innerHTML = ''; // 清空列表
    
    try {
        const response = await fetch(`${API_URL}/warden/students?id=${wardenId}`);
        const data = await response.json();

        // 在控制台打印后端返回的原始数据
        console.log('--- 后端 /warden/students 原始返回数据 ---');
        console.log(data);
        
        if (response.ok && data.success) {
            messageWS.textContent = `Students of ${data.building_id} building information loaded successfully.`;
            messageWS.style.color = 'green';
            if (data.students && data.students.length > 0) {
                data.students.forEach(student => {
                    const row = `
                        <tr class="hover:bg-gray-100">
                            <td>${student.STUDENT_ID}</td>
                            <td>${student.STUDENT_NAME}</td>
                            <td>${student.GENDER}</td>
                            <td>${student.SCHOOL}</td>
                            <td>${student.MAJOR}</td>
                            <td>${student.STUDENT_PHONE_NUM}</td>
                            <td>${student.ROOM_ID}</td>
                            <td>${student.BED_ID}</td>
                            </td>
                        </tr>
                    `;
                    listEl.insertAdjacentHTML('beforeend', row);
                });
            }else {
                listEl.innerHTML = '<tr><td colspan="8" class="text-center py-4">No students found in this building.</td></tr>';
            }
        } else {
            messageWS.textContent = data.message || 'Failed to fetch student info.';
            messageWS.style.color = 'red';
        }
    } catch (error) {
        console.error('获取学生信息时发生网络错误:', error);
        messageWS.textContent = 'Network error, cannot load student info.';
        messageWS.style.color = 'red';
    }
}

async function loadWardenDormInfo(wardenId) {
    if (!document.getElementById('warden-dorm-tab').classList.contains('current-tab')) {
        return; // 如果不在当前 Tab，则不加载，避免不必要的请求
    }
    const messageElem = document.getElementById('warden-dorm-message');
    const totalBedsElem = document.getElementById('summary-total-beds');
    const occupiedBedsElem = document.getElementById('summary-occupied-beds');
    const availableBedsElem = document.getElementById('summary-available-beds');
    const listEl = document.getElementById('warden-dorm-table-body');
    
    messageElem.textContent = 'Loading dorm info...';
    messageElem.style.color = 'gray';
    
    listEl.innerHTML = '';
    
    try {
        const response = await fetch(`${API_URL}/warden/dorm_status?id=${wardenId}`);
        const data = await response.json();

        // 调试：在控制台打印后端返回的原始数据
        console.log('--- 后端 /warden/dorm_status 原始返回数据 ---');
        console.log(data);
       
        if (response.ok && data.success) {
            totalBedsElem.textContent = data.summary.Total_Beds ?? '--';
            occupiedBedsElem.textContent = data.summary.Occupied_Beds ?? '--';
            availableBedsElem.textContent = data.summary.Available_Beds ?? '--';

            const rooms = data.room_status;
            messageElem.textContent = `Rooms of ${data.building_id} building information loaded successfully.`;
            messageElem.style.color = 'green';
            
            if (rooms && rooms.length > 0) {
                listEl.innerHTML = rooms.map(room => {
                    const remaining = room.MAX_CAPACITY - room.GUESTS;
                    const electricity = room.ELECTRICITY_BALANCE?.toFixed(2) ?? '0.00';
                    return `
                        <tr">
                            <td>${room.FLOOR_ID}</td>
                            <td>${room.ROOM_ID}</td>
                            <td>${room.MAX_CAPACITY}</td>
                            <td>${room.GUESTS}</td>
                            <td class="${remaining === 0 ? 'text-red-500 font-semibold' : 'text-green-700'}">${remaining}</td>
                            <td>${electricity}</td>
                        </tr>
                    `;
                }).join('');
            }else {
                listEl.innerHTML = '<tr><td colspan="6" class="text-center py-4">No students found in this building.</td></tr>';
            }
        } else {
            messageElem.textContent = data.message || 'Failed to fetch dorm info.';
            messageElem.style.color = 'red';
        }
    } catch (error) {
        console.error('获取宿舍信息时发生网络错误:', error);
        messageElem.textContent = 'Network error, cannot load dorm info.';
        messageElem.style.color = 'red';
    }
}

async function loadWardenAdjustRequests(wardenId) {
    const tbody = document.getElementById('adjust-table-body');
    tbody.innerHTML = '<tr><td colspan="5" class="text-center">Loading...</td></tr>';

    const adjReqHBProcessed = document.getElementById('summary-adj-req-hbprocessed');
    const adjReqTBProcessed = document.getElementById('summary-adj-req-tbprocessed');
    
    try {
        const res = await fetch(`${API_URL}/warden/pending_adjust_requests?id=${wardenId}`);
        const data = await res.json();
        const info = data.requests_num || {};
        adjReqHBProcessed.textContent = info.WARDEN_HBPROCESSED_REQ_NUM ?? '--';
        adjReqTBProcessed.textContent = info.WARDEN_TBPROCESSED_REQ_NUM ?? '--';
       
        if (res.ok && data.success && data.requests.length > 0) {
            tbody.innerHTML = '';
            data.requests.forEach(req => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${req.STUDENT_ID}</td>
                    <td>${req.STUDENT_NAME}</td>
                    <td>${req.ROOM_ID}</td>
                    <td>${req.TO_ROOM_ID}</td>
                    <td>
                        <button class="btn-action btn-approve" data-request="${req.REQUEST_ID}" data-action="Approve">Approve</button>
                        <button class="btn-action btn-reject" data-request="${req.REQUEST_ID}" data-action="Reject">Reject</button>
                    </td>
                `;
                tbody.appendChild(tr);
            });

            // 按钮事件
            tbody.querySelectorAll('.btn-action').forEach(btn => {
                btn.addEventListener('click', async () => {
                    const requestId = btn.dataset.request;
                    const action = btn.dataset.action;
                    btn.disabled = true;

                    try {
                        const res = await fetch(`${API_URL}/warden/process_adjust_request?id=${wardenId}`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ request_id: requestId, action: action })
                        });
                        const data = await res.json();
                        alert(data.message);
                        if (data.success) {
                            await loadWardenAdjustRequests(wardenId);
                        } else {
                            btn.disabled = false;
                        }
                    } catch (err) {
                        console.error('处理宿舍调整请求失败', err);
                        alert('Network error, processing failed.');
                        btn.disabled = false;
                    }
                });
            });

        } else {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center">No pending requests</td></tr>';
        }
    } catch (err) {
        console.error('加载舍监宿舍调整请求失败', err);
        tbody.innerHTML = '<tr><td colspan="5" class="text-center">Loading failed</td></tr>';
    }
}

// 全局函数

/**
 * 切换手机号的编辑状态 (显示/隐藏表单)。
 * @param {boolean} show - 是否显示编辑表单
 */
function toggleEditPhone(show) {
    const role = localStorage.getItem('role');
    const currentElements = phoneEditElements[role]
    // 检查元素是否存在，防止报错
    if (!currentElements || !currentElements.editBtn || !currentElements.updateForm) {
        console.error(`Error: Phone edit elements not found for role: ${role}`);
        return;
    }
    const editBtn = currentElements.editBtn;
    const updateForm = currentElements.updateForm;
    const input = currentElements.input;
    let infoMessage;

    if (role ==='student'){infoMessage = infoStudentMessage;}
    else if (role ==='tutor'){infoMessage = infoTutorMessage;}
    else if (role ==='warden'){infoMessage = infoWardenMessage;}

    if (show) {
        if (role === 'student'){
            const currentStudentPhone = document.getElementById('info-phone').textContent;
            input.value = currentStudentPhone === 'N/A' ? '' : currentStudentPhone;
        }else if (role === 'tutor'){
            const currentTutorPhone = document.getElementById('info-tutor-phone').textContent;
            input.value = currentTutorPhone === 'N/A' ? '' : currentTutorPhone;
        }else if (role === 'warden'){
            const currentWardenPhone = document.getElementById('info-warden-phone').textContent;
            input.value = currentWardenPhone === 'N/A' ? '' : currentWardenPhone;
        }
        updateForm.classList.remove('hidden');
        editBtn.classList.add('hidden');
        infoMessage.textContent = ''; // 清空提示
        // 确保输入框获得焦点
        if (input) {
            input.focus();
        }
    } else {
        updateForm.classList.add('hidden');
        editBtn.classList.remove('hidden');
        infoMessage.textContent = ''; // 清空提示
    }
}

/**
 * 处理手机号修改表单提交。
 */
async function handleUpdatePhone(event) {
    event.preventDefault();

    let response = null
    const userId = localStorage.getItem('user_id');
    const role = localStorage.getItem('role');
    const currentPhoneInput = phoneEditElements[role].input;
    const newPhone = currentPhoneInput ? currentPhoneInput.value.trim() : '';
    
    if (role ==='student'){infoMessage = infoStudentMessage;}
    else if (role ==='tutor'){infoMessage = infoTutorMessage;}
    else if (role ==='warden'){infoMessage = infoWardenMessage;}
    
    if (!newPhone) {
        infoMessage.textContent = 'Phone number cannot be empty.';
        infoMessage.style.color = 'red';
        return;
    }
    
    const saveBtn = document.querySelector('.save-btn');
    saveBtn.disabled = true;
    saveBtn.textContent = 'Saving...';
    infoMessage.textContent = 'Submitting changes...';
    infoMessage.style.color = 'gray';

    try {
        response = await fetch(`${API_URL}/${role}/update_phone`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: userId, new_phone: newPhone }),
        });
       
        const data = await response.json();

        if (response.ok && data.success) {
            infoMessage.textContent = data.message;
            infoMessage.style.color = 'green';
            // 更新页面显示
            if (role === 'student'){document.getElementById('info-phone').textContent = newPhone;}
            else if (role === 'tutor'){document.getElementById('info-tutor-phone').textContent = newPhone;}
            else if (role === 'warden'){document.getElementById('info-warden-phone').textContent = newPhone;}
            // 隐藏表单
            toggleEditPhone(false);
            
        } else {
            infoMessage.textContent = data.message || 'Failed to update the mobile phone number.';
            infoMessage.style.color = 'red';
        }

    } catch (error) {
        console.error('更新手机号时发生网络错误:', error);
        infoMessage.textContent = 'Network error, cannot connect to server.';
        infoMessage.style.color = 'red';
    } finally {
        saveBtn.disabled = false;
        saveBtn.textContent = 'Save';
    }
}

// 退出登录函数
function logout() {
    localStorage.clear();
    window.location.reload();
}

// 初始化检查和事件监听
document.addEventListener('DOMContentLoaded', () => {
    // 监听登录表单的提交事件
    loginForm.addEventListener('submit', handleLogin);

    // 监听修改手机号按钮的点击事件
    for (const role in phoneEditElements) {
        const elements = phoneEditElements[role];
        if (elements.editBtn) {
            elements.editBtn.addEventListener('click', () => {
                toggleEditPhone(true); 
            });
        }
        // 监听修改手机号表单的提交事件
        if (elements.updateForm) {
            elements.updateForm.addEventListener('submit', handleUpdatePhone);
        }
    }

    // 检查本地存储中是否有已登录的用户
    const savedRole = localStorage.getItem('role');
    const savedUserInfo = localStorage.getItem('user_info');
    
    if (savedRole && savedUserInfo) {
        try {
            const userInfo = JSON.parse(savedUserInfo);
            // 如果存在，直接跳转到仪表盘
            showDashboard(savedRole, userInfo);
            
        } catch (e) {
            console.error('解析用户信息失败:', e);
            logout(); // 解析失败则清除信息并退出
        }
    } else {
        // 否则，保持在登录界面
        loginContainer.classList.remove('hidden');
    }

    const rechargeForm = document.getElementById('electricity-recharge-form');
    if (rechargeForm) {
        rechargeForm.addEventListener('submit', handleRecharge);
    }

    const repairForm = document.getElementById('repair-request-form');
    if (repairForm) {
        // 监听表单提交
        repairForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const roomId = document.getElementById('repair-room').value;
            const repairType = document.getElementById('repair-type').value;
            const messageEl = document.getElementById('repair-message');
            const userId = localStorage.getItem('user_id');
            
            if (!roomId || !repairType) {
                messageEl.textContent = 'Please select the dormitory number and the type of maintenance completely.';
                messageEl.style.color = 'red';
                return;
            }
            
            try {
                const res = await fetch(`${API_URL}/submit_repair_request?id=${userId}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ id: userId, room_id: roomId, repair_type: repairType})
                });
                const data = await res.json();
                messageEl.textContent = data.message;
                messageEl.style.color = data.success ? 'green' : 'red';
            } catch (err) {
                console.error('提交维修申请失败', err);
                messageEl.textContent = 'Network error, fail to submit.';
                messageEl.style.color = 'red';
            }
        });
    }

    const adjustForm = document.getElementById('adjust-request-form');
    if (adjustForm) {
        adjustForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const studentId = localStorage.getItem('user_id');
            const buildingID = document.getElementById('adjust-building').value;
            const floorID = document.getElementById('adjust-floor').value;
            const roomID = document.getElementById('adjust-room').value;
            const bedID = document.getElementById('adjust-bed').value;
            const msgEl = document.getElementById('adjust-message');

            try {
                const res = await fetch(`${API_URL}/student/submit_adjust_request`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ student_id: studentId, building_id: buildingID, floor_id: floorID, room_id: roomID, bed_id: bedID })
                });
                const data = await res.json();
                msgEl.textContent = data.message;
                msgEl.style.color = data.success ? 'green' : 'red';
            } catch (err) {
                console.error('提交调整申请失败', err);
                msgEl.textContent = 'Network error, fail to submit.';
                msgEl.style.color = 'red';
            }
        });
    }
});
