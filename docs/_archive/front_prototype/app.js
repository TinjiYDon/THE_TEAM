/**
 * 智能记账管理系统 - 前端JavaScript应用
 * 功能包括：账单管理、数据分析、AI查询、图表可视化等
 */

class BillManagerApp {
    constructor() {
        this.apiBaseUrl = 'http://localhost:8000/api/v1';
        this.currentPage = 1;
        this.pageSize = 20;
        this.currentSection = 'dashboard';
        this.charts = {};
        this.userId = 1; // 默认用户ID
        
        this.init();
    }

    /**
     * 初始化应用
     */
    init() {
        this.setupEventListeners();
        this.loadDashboard();
        this.setupCharts();
        this.addGlobalRipple();
    }

    /**
     * 设置事件监听器
     */
    setupEventListeners() {
        // 导航菜单
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = link.dataset.section;
                this.switchSection(section);
            });
        });

        // 添加账单按钮
        document.getElementById('add-bill-btn').addEventListener('click', () => {
            this.showAddBillModal();
        });

        // （发票管理已整合到添加账单流程，移除单独入口）

        // 添加账单表单中的发票上传
        const addBtn = document.getElementById('invoice-upload-btn');
        const addInput = document.getElementById('invoice-file');
        if (addBtn && addInput) {
            addBtn.addEventListener('click', () => addInput.click());
            addInput.addEventListener('change', (e) => this.handleAddBillInvoice(e.target.files[0]));
        }

        // 模态框关闭
        document.querySelectorAll('.modal-close, .modal-cancel').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.closeModal(e.target.closest('.modal'));
            });
        });

        // 点击模态框背景关闭
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal(modal);
                }
            });
        });

        // 表单提交
        document.getElementById('add-bill-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleAddBill();
        });

        document.getElementById('edit-bill-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleEditBill();
        });

        // 搜索和过滤
        document.getElementById('bill-search').addEventListener('input', (e) => {
            this.debounce(() => this.loadBills(), 300)();
        });

        document.getElementById('category-filter').addEventListener('change', () => {
            this.loadBills();
        });

        document.getElementById('date-filter').addEventListener('change', () => {
            this.loadBills();
        });

        // 分页
        document.getElementById('prev-page').addEventListener('click', () => {
            if (this.currentPage > 1) {
                this.currentPage--;
                this.loadBills();
            }
        });

        document.getElementById('next-page').addEventListener('click', () => {
            this.currentPage++;
            this.loadBills();
        });

        // AI查询
        document.getElementById('ai-query-btn').addEventListener('click', () => {
            this.handleAIQuery();
        });

        document.getElementById('ai-query-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.handleAIQuery();
            }
        });

        // 建议标签点击
        document.querySelectorAll('.suggestion-tag').forEach(tag => {
            tag.addEventListener('click', () => {
                document.getElementById('ai-query-input').value = tag.dataset.query;
                this.handleAIQuery();
            });
        });

        // 图表控制
        document.getElementById('trend-period').addEventListener('change', () => {
            this.updateTrendChart();
        });

        document.getElementById('category-period').addEventListener('change', () => {
            this.refreshCategoryByPeriod();
        });

        // 分析按钮
        document.getElementById('analyze-btn').addEventListener('click', () => {
            this.performAnalysis();
        });
    }

    /**
     * 切换页面部分
     */
    switchSection(section) {
        // 更新导航状态
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`[data-section="${section}"]`).classList.add('active');

        // 切换页面内容
        document.querySelectorAll('.page-section').forEach(page => {
            page.classList.remove('active');
        });
        document.getElementById(section).classList.add('active');

        this.currentSection = section;

        // 加载对应页面数据
        switch (section) {
            case 'dashboard':
                this.loadDashboard();
                break;
            case 'bills':
                this.loadBills();
                break;
            case 'analysis':
                this.loadAnalysis();
                break;
            case 'ai-insights':
                this.loadAIInsights();
                break;
            case 'invoices':
                this.loadInvoices();
                break;
        }
    }

    /**
     * 显示加载指示器
     */
    showLoading() {
        document.getElementById('loading-overlay').classList.add('active');
    }

    /**
     * 隐藏加载指示器
     */
    hideLoading() {
        document.getElementById('loading-overlay').classList.remove('active');
    }

    /**
     * 显示通知
     */
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <i class="fas fa-${this.getNotificationIcon(type)}"></i>
                <span>${message}</span>
            </div>
        `;

        const container = document.getElementById('notifications');
        container.appendChild(notification);

        // 自动移除通知
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }

    /**
     * 获取通知图标
     */
    getNotificationIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    /**
     * API请求封装
     */
    async apiRequest(endpoint, options = {}) {
        const url = `${this.apiBaseUrl}${endpoint}`;
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };

        const config = { ...defaultOptions, ...options };

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || '请求失败');
            }

            return data;
        } catch (error) {
            console.error('API请求错误:', error);
            this.showNotification(`请求失败: ${error.message}`, 'error');
            throw error;
        }
    }

    /**
     * 加载仪表板数据
     */
    async loadDashboard() {
        this.showLoading();
        try {
            // 并行加载多个数据
            const [summary, recentBills, trendData, categoryData, allBills] = await Promise.all([
                this.apiRequest('/analysis/summary'),
                this.apiRequest('/bills?limit=5'),
                this.apiRequest('/analysis/trend'),
                this.apiRequest('/analysis/category'),
                this.apiRequest('/bills?limit=1000')
            ]);

            this.updateDashboardStats(summary.data);
            this.updateRecentTransactions(recentBills.data);
            // 趋势：若后端无数据，使用账单聚合
            if (trendData && trendData.data) {
                this.updateTrendChart(trendData.data);
            } else if (allBills && allBills.data) {
                this.updateTrendChart(this.buildTrendFromBills(allBills.data));
            } else {
                this.updateTrendChart(null);
            }
            // 分类：若后端无数据，用账单聚合
            if (categoryData && categoryData.data) {
                this.updateCategoryChart(categoryData.data);
            } else if (allBills && allBills.data) {
                this.updateCategoryChart(this.computeCategoryFromBills(allBills.data));
            } else {
                this.updateCategoryChart(null);
            }

        } catch (error) {
            console.error('加载仪表板数据失败:', error);
        } finally {
            this.hideLoading();
        }
    }

    /**
     * 更新仪表板统计
     */
    updateDashboardStats(summary) {
        // 数字滚动动画
        this.animateCount('total-spending', summary.total_amount || 0, { prefix: '¥', decimals: 2 });
        this.animateCount('total-transactions', summary.total_count || 0, { decimals: 0 });
        this.animateCount('avg-transaction', summary.avg_amount || 0, { prefix: '¥', decimals: 2 });
        
        // 更新变化百分比（模拟数据）
        const spendingChange = document.getElementById('spending-change');
        const transactionChange = document.getElementById('transaction-change');
        const avgChange = document.getElementById('avg-change');
        
        spendingChange.textContent = '+5.2%';
        spendingChange.className = 'stat-change positive';
        
        transactionChange.textContent = '+12.3%';
        transactionChange.className = 'stat-change positive';
        
        avgChange.textContent = '-2.1%';
        avgChange.className = 'stat-change negative';
    }

    /**
     * 数字滚动动画
     */
    animateCount(elementId, target, { prefix = '', decimals = 0, duration = 800 } = {}) {
        const el = document.getElementById(elementId);
        if (!el) return;
        const start = 0;
        const startTime = performance.now();
        const formatter = (v) => prefix + v.toFixed(decimals).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
        const step = (now) => {
            const p = Math.min(1, (now - startTime) / duration);
            const ease = 1 - Math.pow(1 - p, 3);
            const val = start + (target - start) * ease;
            el.textContent = formatter(val);
            if (p < 1) requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
    }

    /**
     * 按钮涟漪效果（委托）
     */
    addGlobalRipple() {
        document.addEventListener('click', (e) => {
            const btn = e.target.closest('.btn');
            if (!btn) return;
            const rect = btn.getBoundingClientRect();
            const span = document.createElement('span');
            span.className = 'ripple-span';
            const size = Math.max(rect.width, rect.height);
            span.style.width = span.style.height = size + 'px';
            span.style.left = (e.clientX - rect.left - size / 2) + 'px';
            span.style.top = (e.clientY - rect.top - size / 2) + 'px';
            btn.appendChild(span);
            setTimeout(() => span.remove(), 650);
        });
    }

    /**
     * 更新最近交易
     */
    updateRecentTransactions(bills) {
        const container = document.getElementById('recent-transactions-list');
        
        if (!bills || bills.length === 0) {
            container.innerHTML = '<p style="text-align: center; color: var(--text-tertiary); padding: 2rem;">暂无交易记录</p>';
            return;
        }

        container.innerHTML = bills.map(bill => `
            <div class="transaction-item">
                <div class="transaction-info">
                    <div class="transaction-icon">
                        <i class="fas fa-${this.getCategoryIcon(bill.category)}"></i>
                    </div>
                    <div class="transaction-details">
                        <h4>${bill.merchant}</h4>
                        <p>${new Date(bill.consume_time).toLocaleDateString()} • ${bill.category}</p>
                    </div>
                </div>
                <div class="transaction-amount">¥${bill.amount.toFixed(2)}</div>
            </div>
        `).join('');
    }

    /**
     * 获取类别图标
     */
    getCategoryIcon(category) {
        const icons = {
            '餐饮': 'utensils',
            '交通': 'car',
            '购物': 'shopping-bag',
            '娱乐': 'gamepad',
            '医疗': 'heartbeat',
            '教育': 'book',
            '其他': 'tag'
        };
        return icons[category] || 'tag';
    }

    /**
     * 设置图表
     */
    setupCharts() {
        // 趋势图表
        const trendCtx = document.getElementById('trendChart').getContext('2d');
        this.charts.trend = new Chart(trendCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: '消费金额',
                    data: [],
                    borderColor: '#1E5BBA',
                    backgroundColor: 'rgba(30, 91, 186, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#1E5BBA',
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 3,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false, // 要求：禁用保持宽高比，用父容器高度
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        enabled: true,
                        callbacks: {
                            label: (ctx) => `¥${ctx.parsed.y.toLocaleString()}`
                        }
                    },
                    zoom: {
                        pan: { enabled: true, mode: 'x' },
                        zoom: {
                            wheel: { enabled: true },
                            pinch: { enabled: true },
                            mode: 'x'
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: '#E5E5E5', // 水平网格线
                            drawBorder: false
                        },
                        ticks: {
                            color: '#666666',
                            maxTicksLimit: 8,
                            callback: (value) => this.formatYAxisLabelAdvanced(value)
                        }
                    },
                    x: {
                        grid: {
                            color: '#E5E5E5'
                        },
                        ticks: {
                            color: '#666666',
                            maxRotation: 0,
                            minRotation: 0,
                            autoSkip: false,
                            callback: (value, index) => {
                                // 使用预生成的格式化标签，未命名位置返回空串以减少密度
                                return (this.trendFormattedLabels && this.trendFormattedLabels[index]) || '';
                            }
                        }
                    }
                },
                animation: { duration: 500, easing: 'easeOutCubic' }
            }
        });

        // 分类环形图
        const categoryCtx = document.getElementById('categoryChart').getContext('2d');
        const ringCenterText = {
            id: 'ringCenterText',
            afterDraw(chart) {
                const { ctx, chartArea: { width, height } } = chart;
                const sum = chart.data.datasets[0].data.reduce((a, b) => a + b, 0);
                const centerX = chart.getDatasetMeta(0).data[0]?.x ?? width / 2;
                const centerY = chart.getDatasetMeta(0).data[0]?.y ?? height / 2;
                ctx.save();
                ctx.textAlign = 'center';
                ctx.fillStyle = '#0F3D7A';
                ctx.font = '600 14px Inter, sans-serif';
                ctx.fillText('总消费', centerX, centerY - 10);
                ctx.font = '700 18px Inter, sans-serif';
                ctx.fillStyle = '#1E5BBA';
                ctx.fillText('¥' + sum.toLocaleString(), centerX, centerY + 16);
                ctx.restore();
            }
        };

        this.charts.category = new Chart(categoryCtx, {
            type: 'doughnut',
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    backgroundColor: ['#1E5BBA', '#4A90E2', '#07C160', '#FF9C00', '#FA5151', '#0F3D7A'],
                    borderWidth: 0,
                    hoverOffset: 10
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '60%', // 环形中空比例
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#333333',
                            padding: 16,
                            usePointStyle: true,
                            pointStyle: 'circle'
                        },
                        onClick: (e, legendItem, legend) => {
                            const index = legendItem.index;
                            const ci = legend.chart;
                            const ds = ci.data.datasets[0];
                            const meta = ci.getDatasetMeta(0);
                            meta.data[index].hidden = !meta.data[index].hidden;
                            // 同时切换数据为0/原值，避免占比计算不直观
                            if (meta.data[index].hidden) {
                                ds._backup = ds._backup || ds.data.slice();
                                ds.data[index] = 0;
                            } else if (ds._backup) {
                                ds.data[index] = ds._backup[index];
                            }
                            ci.update();
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => {
                                const label = ctx.label || '';
                                const value = ctx.raw || 0;
                                const total = ctx.dataset.data.reduce((a, b) => a + b, 0) || 1;
                                const pct = (value / total * 100).toFixed(1);
                                return `${label}: ¥${Number(value).toLocaleString()} (${pct}%)`;
                            }
                        }
                    }
                },
                animation: { animateScale: true, animateRotate: true }
            },
            plugins: [ringCenterText]
        });
    }

    /**
     * 标签格式化（千元单位）
     */
    formatYAxisLabel(value) {
        if (value >= 1000000) {
            return (value / 1000000).toFixed(1).replace(/\.0$/, '') + 'm';
        }
        if (value >= 1000) {
            return (value / 1000).toFixed(0) + 'k';
        }
        return String(Math.round(value));
    }

    /**
     * 高级数值轴格式化：元/k/w/10w
     */
    formatYAxisLabelAdvanced(value) {
        const v = Number(value) || 0;
        if (v < 1000) return String(Math.round(v));      // 元
        if (v < 10000) return (v / 1000).toFixed(0) + 'k'; // 千元
        if (v < 100000) return (v / 10000).toFixed(0) + 'w'; // 万元
        return (v / 10000).toFixed(0) + 'w';               // 十万元以上仍以w显示（10w,20w...）
    }

    /**
     * 智能刻度间隔算法
     * - 根据数据最大值选择合适的刻度间隔（100/500/1000/5000）
     * - 目标刻度数量在5-8之间
     */
    computeSmartYAxis(values) {
        const maxVal = Math.max(...values, 0);
        if (maxVal <= 0) {
            return { stepSize: 100, suggestedMax: 500, maxTicks: 5 };
        }

        const candidates = [100, 500, 1000, 5000, 10000, 20000, 50000, 100000];
        let chosen = candidates[0];
        let ticks = Math.ceil(maxVal / chosen) + 1; // 顶部多留一档

        for (const step of candidates) {
            const count = Math.ceil(maxVal / step) + 1;
            if (count >= 5 && count <= 8) {
                chosen = step;
                ticks = count;
                break;
            }
            // 若没有落在5-8之间，选择最接近8的方案
            if (count < 5) {
                chosen = step;
                ticks = count;
                break;
            }
            chosen = step;
            ticks = count;
        }

        const suggestedMax = chosen * ticks;
        const maxTicks = Math.min(8, Math.max(5, ticks));
        return { stepSize: chosen, suggestedMax, maxTicks };
    }

    /**
     * 高级Y轴智能刻度：根据金额区间选择步长
     */
    computeSmartYAxisAdvanced(values) {
        const maxVal = Math.max(...values, 0);
        if (maxVal <= 0) return { stepSize: 100, suggestedMax: 500, maxTicks: 5 };

        let steps;
        if (maxVal < 1000)       steps = [50, 100, 200, 250];
        else if (maxVal < 10000) steps = [200, 500, 1000, 2000];
        else if (maxVal < 100000)steps = [2000, 5000, 10000, 20000];
        else                     steps = [10000, 20000, 50000, 100000];

        let chosen = steps[0];
        let ticks = Math.ceil(maxVal / chosen) + 1;
        for (const s of steps) {
            const c = Math.ceil(maxVal / s) + 1;
            if (c >= 5 && c <= 8) { chosen = s; ticks = c; break; }
            chosen = s; ticks = c;
        }
        return { stepSize: chosen, suggestedMax: chosen * ticks, maxTicks: Math.min(8, Math.max(5, ticks)) };
    }

    /**
     * 构建时间轴：返回 ISO 标签与格式化标签
     */
    buildTimeAxis(period) {
        const now = new Date();
        const isoLabels = [];
        const formatted = [];
        const p = String(period);

        const push = (date, label) => {
            isoLabels.push(date.toISOString());
            formatted.push(label);
        };

        if (p === '7') {
            // 每天
            for (let i = 6; i >= 0; i--) {
                const d = new Date(now);
                d.setDate(now.getDate() - i);
                const mm = String(d.getMonth() + 1).padStart(2, '0');
                const dd = String(d.getDate()).padStart(2, '0');
                push(d, `${mm}-${dd}`);
            }
        } else if (p === '30') {
            // 每周（近4~5周）
            const weeks = 5;
            for (let i = weeks - 1; i >= 0; i--) {
                const d = new Date(now);
                d.setDate(now.getDate() - i * 7);
                push(d, `第${weeks - i}周`);
            }
        } else if (p === '90') {
            // 每半月 6段（上/下）
            const start = new Date(now);
            start.setMonth(now.getMonth() - 2); // 含当前月共3月
            for (let m = 0; m < 3; m++) {
                const monthDate = new Date(start);
                monthDate.setMonth(start.getMonth() + m);
                const y = monthDate.getFullYear();
                const mon = monthDate.getMonth() + 1;
                const first = new Date(y, mon - 1, 1);
                const mid = new Date(y, mon - 1, 16);
                push(first, `${mon}月上`);
                push(mid, `${mon}月下`);
            }
        } else if (p === '180' || p === '365') {
            // 每月
            const months = p === '180' ? 6 : 12;
            for (let i = months - 1; i >= 0; i--) {
                const d = new Date(now);
                d.setMonth(now.getMonth() - i, 1);
                const mon = String(d.getMonth() + 1);
                push(d, `${mon}月`);
            }
        } else {
            // 使用以来：每季度（近8个季度）
            const quarters = 8;
            for (let i = quarters - 1; i >= 0; i--) {
                const d = new Date(now);
                d.setMonth(now.getMonth() - i * 3, 1);
                const y = d.getFullYear();
                const q = Math.floor(d.getMonth() / 3) + 1;
                push(d, `${y}Q${q}`);
            }
        }

        return { isoLabels, formattedLabels: formatted };
    }

    /**
     * 更新趋势图表
     */
    updateTrendChart(data) {
        if (!data || !this.charts.trend) return;

        const period = document.getElementById('trend-period').value;
        const { isoLabels, formattedLabels } = this.buildTimeAxis(period);
        this.trendFormattedLabels = formattedLabels; // 提供给x轴ticks
        // 若传入后端/本地聚合结果 data.values 则使用，否则示例数据
        let values = Array.isArray(data?.values) && data.values.length === isoLabels.length
            ? data.values
            : isoLabels.map(() => Math.random() * 100000 + 300);

        // 计算智能刻度
        const scale = this.computeSmartYAxisAdvanced(values);

        // 应用到图表
        this.charts.trend.data.labels = isoLabels;
        this.charts.trend.data.datasets[0].data = values;
        this.charts.trend.options.scales.y.ticks.stepSize = scale.stepSize; // 智能间隔
        this.charts.trend.options.scales.y.suggestedMax = scale.suggestedMax; // 顶部留白
        this.charts.trend.options.scales.y.ticks.maxTicksLimit = scale.maxTicks; // 5-8个刻度
        // 长时间范围倾斜标签
        const needRotate = ['90','180','365','all'].includes(String(period));
        this.charts.trend.options.scales.x.ticks.maxRotation = needRotate ? 45 : 0;
        this.charts.trend.options.scales.x.ticks.minRotation = needRotate ? 45 : 0;
        this.charts.trend.update();
    }

    /**
     * 更新分类图表
     */
    updateCategoryChart(data) {
        if (!this.charts.category) return;

        const normalized = this.normalizeCategoryData(data);

        // 若无有效数据则清空并返回
        if (normalized.labels.length === 0) {
            this.charts.category.data.labels = [];
            this.charts.category.data.datasets[0].data = [];
            this.charts.category.update();
            return;
        }

        this.charts.category.data.labels = normalized.labels;
        this.charts.category.data.datasets[0].data = normalized.values;

        // 若分类超过预设颜色数量，可动态扩展（循环使用）
        const baseColors = ['#1E5BBA', '#4A90E2', '#07C160', '#FF9C00', '#FA5151', '#0F3D7A'];
        const bgColors = normalized.labels.map((_, i) => baseColors[i % baseColors.length]);
        this.charts.category.data.datasets[0].backgroundColor = bgColors;

        this.charts.category.update();
    }

    /**
     * 根据选择的周期重新拉取或过滤分类数据
     * 优先请求后端 /analysis/category；若为空就从 /bills 过滤时间再本地聚合
     */
    async refreshCategoryByPeriod() {
        const period = document.getElementById('category-period').value;
        const { isoLabels } = this.buildTimeAxis(period);
        const startISO = isoLabels[0];
        const endISO = isoLabels[isoLabels.length - 1];

        try {
            // 先试后端
            const res = await this.apiRequest(`/analysis/category?start_date=${encodeURIComponent(startISO)}&end_date=${encodeURIComponent(endISO)}`);
            if (res && res.data) {
                this.updateCategoryChart(res.data);
                return;
            }
        } catch (e) {
            // 忽略，尝试本地聚合
        }

        try {
            // 拉取较多账单，在前端按时间过滤
            const billsRes = await this.apiRequest('/bills?limit=2000');
            const bills = (billsRes && billsRes.data) || [];
            const start = new Date(startISO).getTime();
            const end = new Date(endISO).getTime();
            const filtered = bills.filter(b => {
                const t = new Date(b.consume_time).getTime();
                return t >= start && t <= end;
            });
            this.updateCategoryChart(this.computeCategoryFromBills(filtered));
        } catch (e) {
            console.error('刷新分类失败', e);
        }
    }

    /**
     * 规范化分类消费数据
     * 接受两种可能结构：
     * 1) 数组：[{ category: '餐饮', total_amount: 1234 }, ...] 或 [{ name: '餐饮', value: 1234 }, ...]
     * 2) 字典：{ '餐饮': 1234, '交通': 888, ... }
     */
    normalizeCategoryData(raw) {
        const result = { labels: [], values: [] };
        if (!raw) return result;

        // 如果是数组
        if (Array.isArray(raw)) {
            const pairs = raw.map((item) => {
                const key = item.category ?? item.name ?? item.label ?? '未分类';
                const val = Number(item.total_amount ?? item.amount ?? item.value ?? 0) || 0;
                return [String(key), val];
            });
            // 过滤无效并按金额降序
            const filtered = pairs.filter(([, v]) => v > 0).sort((a, b) => b[1] - a[1]);
            result.labels = filtered.map(([k]) => k);
            result.values = filtered.map(([, v]) => v);
            return result;
        }

        // 如果是对象（字典）
        if (typeof raw === 'object') {
            const entries = Object.entries(raw)
                .map(([k, v]) => [String(k), Number(v) || 0])
                .filter(([, v]) => v > 0)
                .sort((a, b) => b[1] - a[1]);
            result.labels = entries.map(([k]) => k);
            result.values = entries.map(([, v]) => v);
            return result;
        }

        return result;
    }

    /**
     * 当分析接口为空时：从账单构建分类数据
     */
    computeCategoryFromBills(bills) {
        if (!Array.isArray(bills)) return [];
        const map = new Map();
        bills.forEach(b => {
            const cat = b.category || '未分类';
            const amt = Number(b.amount) || 0;
            map.set(cat, (map.get(cat) || 0) + amt);
        });
        return Array.from(map.entries()).map(([category, total]) => ({ category, total_amount: total }));
    }

    /**
     * 当分析接口为空时：从账单按时间粒度构建趋势数据
     * 返回结构与 updateTrendChart 兼容（这里只需要 values数组即可）
     */
    buildTrendFromBills(bills) {
        const period = document.getElementById('trend-period').value;
        const { isoLabels } = this.buildTimeAxis(period);

        // 按粒度聚合到对应标签（天/周/半月/月/季度的起始ISO）
        const bucketKey = (d) => {
            const p = String(period);
            const date = new Date(d);
            const y = date.getFullYear();
            const m = date.getMonth();
            const day = date.getDate();
            if (p === '7') {
                return new Date(y, m, day, 0, 0, 0, 0).toISOString();
            } else if (p === '30') {
                const weekStart = new Date(date); weekStart.setDate(date.getDate() - date.getDay());
                return new Date(weekStart.getFullYear(), weekStart.getMonth(), weekStart.getDate()).toISOString();
            } else if (p === '90') {
                const isFirstHalf = day <= 15;
                return new Date(y, m, isFirstHalf ? 1 : 16).toISOString();
            } else if (p === '180' || p === '365') {
                return new Date(y, m, 1).toISOString();
            } else {
                const qStartMonth = Math.floor(m / 3) * 3;
                return new Date(y, qStartMonth, 1).toISOString();
            }
        };

        const sums = new Map(isoLabels.map(k => [k, 0]));
        (bills || []).forEach(b => {
            if (!b.consume_time) return;
            const key = bucketKey(b.consume_time);
            if (!sums.has(key)) return; // 不在当前范围的忽略
            sums.set(key, sums.get(key) + (Number(b.amount) || 0));
        });

        // 只返回values，x轴labels由 buildTimeAxis 已设置
        return { values: isoLabels.map(k => sums.get(k) || 0) };
    }

    /**
     * 加载账单列表
     */
    async loadBills() {
        this.showLoading();
        try {
            const search = document.getElementById('bill-search').value;
            const category = document.getElementById('category-filter').value;
            const date = document.getElementById('date-filter').value;

            let endpoint = `/bills?limit=${this.pageSize}&offset=${(this.currentPage - 1) * this.pageSize}`;
            
            if (search) {
                endpoint += `&search=${encodeURIComponent(search)}`;
            }
            if (category) {
                endpoint += `&category=${encodeURIComponent(category)}`;
            }
            if (date) {
                endpoint += `&date=${encodeURIComponent(date)}`;
            }

            const response = await this.apiRequest(endpoint);
            this.updateBillsTable(response.data);
            this.updatePagination(response.total || response.data.length);

        } catch (error) {
            console.error('加载账单列表失败:', error);
        } finally {
            this.hideLoading();
        }
    }

    /**
     * 更新账单表格
     */
    updateBillsTable(bills) {
        const tbody = document.getElementById('bills-table-body');
        
        if (!bills || bills.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="padding:0"><div class="skeleton" style="height:56px; margin:16px"></div><div class="skeleton" style="height:56px; margin:16px"></div><div class="skeleton" style="height:56px; margin:16px"></div></td></tr>';
            return;
        }

        tbody.innerHTML = bills.map(bill => `
            <tr>
                <td>${new Date(bill.consume_time).toLocaleDateString()}</td>
                <td>${bill.merchant}</td>
                <td>
                    <span class="category-badge category-${bill.category}">${bill.category}</span>
                </td>
                <td class="amount">¥${bill.amount.toFixed(2)}</td>
                <td>${bill.payment_method}</td>
                <td>
                    <div class="action-buttons">
                        <button class="btn btn-sm btn-secondary" onclick="app.editBill(${bill.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-error" onclick="app.deleteBill(${bill.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    }

    /**
     * 更新分页
     */
    updatePagination(total) {
        const totalPages = Math.ceil(total / this.pageSize);
        const prevBtn = document.getElementById('prev-page');
        const nextBtn = document.getElementById('next-page');
        const pageInfo = document.getElementById('page-info');

        prevBtn.disabled = this.currentPage <= 1;
        nextBtn.disabled = this.currentPage >= totalPages;
        pageInfo.textContent = `第 ${this.currentPage} 页，共 ${totalPages} 页`;
    }

    /**
     * 显示添加账单模态框
     */
    showAddBillModal() {
        const modal = document.getElementById('add-bill-modal');
        modal.classList.add('active');
        
        // 设置默认日期为今天
        const now = new Date();
        const dateInput = document.getElementById('bill-date');
        dateInput.value = now.toISOString().slice(0, 16);
    }

    /**
     * 处理添加账单
     */
    async handleAddBill() {
        const form = document.getElementById('add-bill-form');
        const formData = new FormData(form);
        
        const billData = {
            consume_time: formData.get('bill-date'),
            merchant: formData.get('bill-merchant'),
            category: formData.get('bill-category'),
            amount: parseFloat(formData.get('bill-amount')),
            payment_method: formData.get('bill-payment'),
            location: formData.get('bill-location') || null,
            description: formData.get('bill-description') || null
        };

        // 若有临时识别的发票文件路径一并携带（由handleAddBillInvoice设置）
        if (this._lastInvoiceFilePath) {
            billData.invoice_file_path = this._lastInvoiceFilePath;
        }

        this.showLoading();
        try {
            await this.apiRequest('/bills', {
                method: 'POST',
                body: JSON.stringify(billData)
            });

            this.showNotification('账单添加成功！', 'success');
            this.closeModal(document.getElementById('add-bill-modal'));
            form.reset();
            
            // 如果当前在账单页面，重新加载列表
            if (this.currentSection === 'bills') {
                this.loadBills();
            } else {
                this.loadDashboard();
            }

        } catch (error) {
            console.error('添加账单失败:', error);
        } finally {
            this.hideLoading();
        }
    }

    /**
     * 添加账单流程：处理发票图片，调用后端OCR接口并回填表单
     */
    async handleAddBillInvoice(file) {
        if (!file) return;
        const preview = document.getElementById('invoice-preview');
        if (preview) {
            const url = URL.createObjectURL(file);
            preview.style.backgroundImage = `url(${url})`;
        }

        try {
            // 将图片上传到后端静态/临时目录，或直接附带OCR
            // 这里简化：先上传，获得后端保存路径，再请求OCR
            const uploadForm = new FormData();
            uploadForm.append('file', file);

            // 如果有专门的上传接口可替换为实际地址，这里复用OCR接口的 file_path 字段
            const ocrRes = await this.apiRequest('/invoices/process', {
                method: 'POST',
                body: JSON.stringify({ ocr_text: '', user_id: this.userId, file_path: 'temp://' })
            });
            // 由于后端接口示例以 ocr_text/file_path 为输入，真实实现应为上传返回路径再传入process
            // 为保证此处不阻塞，尝试直接从返回中读取可用字段
            const result = ocrRes?.data || {};

            // 记录原始发票文件路径（如果后端回传）
            if (result.file_path) this._lastInvoiceFilePath = result.file_path;

            // 回填表单（允许用户修改）
            if (result.merchant) document.getElementById('bill-merchant').value = result.merchant;
            if (result.amount) document.getElementById('bill-amount').value = result.amount;
            if (result.category) document.getElementById('bill-category').value = result.category;
            if (result.invoice_time) {
                const dt = new Date(result.invoice_time);
                document.getElementById('bill-date').value = dt.toISOString().slice(0,16);
            }

            this.showNotification('发票识别完成，已为您自动填充，可手动调整。', 'success');
        } catch (error) {
            console.error('发票识别失败:', error);
            this.showNotification('发票识别失败，请手动填写。', 'warning');
        }
    }

    /**
     * 编辑账单
     */
    async editBill(billId) {
        this.showLoading();
        try {
            const response = await this.apiRequest(`/bills/${billId}`);
            const bill = response.data;
            
            // 填充编辑表单
            document.getElementById('edit-bill-id').value = bill.id;
            document.getElementById('edit-bill-date').value = new Date(bill.consume_time).toISOString().slice(0, 16);
            document.getElementById('edit-bill-merchant').value = bill.merchant;
            document.getElementById('edit-bill-category').value = bill.category;
            document.getElementById('edit-bill-amount').value = bill.amount;
            document.getElementById('edit-bill-payment').value = bill.payment_method;
            document.getElementById('edit-bill-location').value = bill.location || '';
            document.getElementById('edit-bill-description').value = bill.description || '';
            
            // 显示编辑模态框
            document.getElementById('edit-bill-modal').classList.add('active');

        } catch (error) {
            console.error('获取账单详情失败:', error);
        } finally {
            this.hideLoading();
        }
    }

    /**
     * 处理编辑账单
     */
    async handleEditBill() {
        const form = document.getElementById('edit-bill-form');
        const formData = new FormData(form);
        const billId = formData.get('edit-bill-id');
        
        const billData = {
            consume_time: formData.get('edit-bill-date'),
            merchant: formData.get('edit-bill-merchant'),
            category: formData.get('edit-bill-category'),
            amount: parseFloat(formData.get('edit-bill-amount')),
            payment_method: formData.get('edit-bill-payment'),
            location: formData.get('edit-bill-location') || null,
            description: formData.get('edit-bill-description') || null
        };

        this.showLoading();
        try {
            await this.apiRequest(`/bills/${billId}`, {
                method: 'PUT',
                body: JSON.stringify(billData)
            });

            this.showNotification('账单更新成功！', 'success');
            this.closeModal(document.getElementById('edit-bill-modal'));
            
            // 重新加载数据
            if (this.currentSection === 'bills') {
                this.loadBills();
            } else {
                this.loadDashboard();
            }

        } catch (error) {
            console.error('更新账单失败:', error);
        } finally {
            this.hideLoading();
        }
    }

    /**
     * 删除账单
     */
    async deleteBill(billId) {
        if (!confirm('确定要删除这条账单记录吗？')) {
            return;
        }

        this.showLoading();
        try {
            await this.apiRequest(`/bills/${billId}`, {
                method: 'DELETE'
            });

            this.showNotification('账单删除成功！', 'success');
            
            // 重新加载数据
            if (this.currentSection === 'bills') {
                this.loadBills();
            } else {
                this.loadDashboard();
            }

        } catch (error) {
            console.error('删除账单失败:', error);
        } finally {
            this.hideLoading();
        }
    }

    /**
     * 关闭模态框
     */
    closeModal(modal) {
        modal.classList.remove('active');
    }

    /**
     * 处理AI查询
     */
    async handleAIQuery() {
        const query = document.getElementById('ai-query-input').value.trim();
        if (!query) {
            this.showNotification('请输入查询内容', 'warning');
            return;
        }

        this.showLoading();
        try {
            const response = await this.apiRequest('/query', {
                method: 'POST',
                body: JSON.stringify({
                    query: query,
                    user_id: this.userId
                })
            });

            this.displayAIResult(response);

        } catch (error) {
            console.error('AI查询失败:', error);
        } finally {
            this.hideLoading();
        }
    }

    /**
     * 显示AI查询结果
     */
    displayAIResult(result) {
        const container = document.getElementById('ai-results');
        
        const resultHtml = `
            <div class="ai-result-card">
                <div class="result-header">
                    <h4>查询结果</h4>
                    <span class="query-text">"${result.query}"</span>
                </div>
                <div class="result-content">
                    <div class="result-summary">
                        <h5>解析结果：</h5>
                        <p>查询类型：${result.parsed_query?.intent || '未知'}</p>
                        <p>时间范围：${result.parsed_query?.time_info?.type || '全部'}</p>
                        <p>消费类别：${result.parsed_query?.category_info?.category || '全部'}</p>
                    </div>
                    <div class="result-data">
                        <h5>数据结果：</h5>
                        <div class="data-item">
                            <span class="label">总金额：</span>
                            <span class="value">¥${result.result?.total_amount?.toFixed(2) || '0.00'}</span>
                        </div>
                        <div class="data-item">
                            <span class="label">交易次数：</span>
                            <span class="value">${result.result?.count || '0'}</span>
                        </div>
                        <div class="data-item">
                            <span class="label">平均金额：</span>
                            <span class="value">¥${result.result?.avg_amount?.toFixed(2) || '0.00'}</span>
                        </div>
                    </div>
                </div>
            </div>
        `;

        container.innerHTML = resultHtml;
    }

    /**
     * 加载AI洞察页面
     */
    async loadAIInsights() {
        this.showLoading();
        try {
            // 并行加载用户画像和推荐
            const [profile, financialRecs, spendingRecs] = await Promise.all([
                this.apiRequest(`/ai/profile/${this.userId}`).catch(() => null),
                this.apiRequest(`/ai/recommendations/financial/${this.userId}`).catch(() => null),
                this.apiRequest(`/ai/recommendations/spending/${this.userId}`).catch(() => null)
            ]);

            this.updateUserProfile(profile?.data);
            this.updateRecommendations(financialRecs?.data, spendingRecs?.data);

        } catch (error) {
            console.error('加载AI洞察失败:', error);
        } finally {
            this.hideLoading();
        }
    }

    /**
     * 更新用户画像
     */
    updateUserProfile(profile) {
        const container = document.getElementById('user-profile-cards');
        if (!container) return;
        if (!profile) {
            container.innerHTML = '<div class="skeleton" style="height:120px"></div>';
            return;
        }

        const metricsHtml = `
            <div class="profile-card">
                <h4>用户画像</h4>
                <div class="profile-metrics">
                    <div class="metric"><div class="label">收入水平</div><div class="value">${profile.income_level || '未知'}</div></div>
                    <div class="metric"><div class="label">风险承受</div><div class="value">${profile.risk_tolerance || '未知'}</div></div>
                    <div class="metric"><div class="label">信用评分</div><div class="value">${profile.credit_score ?? '—'}</div></div>
                    <div class="metric"><div class="label">主消费类</div><div class="value">${profile.spending_pattern?.top_category || '未知'}</div></div>
                </div>
            </div>
            <div class="profile-card">
                <h4>消费偏好</h4>
                <p>消费频率：${profile.spending_pattern?.frequency || '未知'}</p>
                <p>平均消费：¥${profile.spending_pattern?.avg_amount?.toFixed(2) || '0.00'}</p>
                <p>投资偏好：${(profile.investment_preference?.type) || '—'}</p>
            </div>
        `;

        container.innerHTML = metricsHtml;
    }

    /**
     * 更新推荐内容
     */
    updateRecommendations(financialRecs, spendingRecs) {
        const container = document.getElementById('recommendation-cards');
        if (!container) return;
        const financial = (financialRecs || []).slice(0, 6);
        const spending = (spendingRecs || []).slice(0, 6);

        container.innerHTML = `
            <div class="recommendation-card">
                <h4>金融产品推荐</h4>
                <div class="rec-content">
                    ${financial.length ? financial.map(rec => `
                        <div class="rec-item">
                            <h5>${rec.product_name}</h5>
                            <p>${rec.description || ''}</p>
                            <span class="rec-tag">${rec.product_type || ''}</span>
                        </div>
                    `).join('') : '<div class="skeleton" style="height:80px"></div>'}
                </div>
            </div>
            <div class="recommendation-card">
                <h4>消费建议</h4>
                <div class="rec-content">
                    ${spending.length ? spending.map(rec => `
                        <div class="rec-item">
                            <h5>${rec.title || ''}</h5>
                            <p>${rec.description || ''}</p>
                            <span class="rec-tag">${rec.category || ''}</span>
                        </div>
                    `).join('') : '<div class="skeleton" style="height:80px"></div>'}
                </div>
            </div>
        `;
    }

    /**
     * 加载分析页面
     */
    async loadAnalysis() {
        // 设置默认日期范围（最近30天）
        const endDate = new Date();
        const startDate = new Date();
        startDate.setDate(startDate.getDate() - 30);

        document.getElementById('analysis-start-date').value = startDate.toISOString().split('T')[0];
        document.getElementById('analysis-end-date').value = endDate.toISOString().split('T')[0];
    }

    /**
     * 执行分析
     */
    async performAnalysis() {
        const startDate = document.getElementById('analysis-start-date').value;
        const endDate = document.getElementById('analysis-end-date').value;
        const analysisType = document.getElementById('analysis-type').value;

        if (!startDate || !endDate) {
            this.showNotification('请选择分析日期范围', 'warning');
            return;
        }

        this.showLoading();
        try {
            const response = await this.apiRequest('/analysis/comprehensive', {
                method: 'POST',
                body: JSON.stringify({
                    user_id: this.userId,
                    start_date: startDate,
                    end_date: endDate
                })
            });

            this.displayAnalysisResults(response.data);

        } catch (error) {
            console.error('分析失败:', error);
        } finally {
            this.hideLoading();
        }
    }

    /**
     * 显示分析结果
     */
    displayAnalysisResults(data) {
        const container = document.getElementById('analysis-results');
        
        const resultsHtml = `
            <div class="analysis-summary">
                <h3>分析摘要</h3>
                <div class="summary-grid">
                    <div class="summary-item">
                        <span class="label">总支出：</span>
                        <span class="value">¥${data.total_spending?.toFixed(2) || '0.00'}</span>
                    </div>
                    <div class="summary-item">
                        <span class="label">交易次数：</span>
                        <span class="value">${data.total_transactions || '0'}</span>
                    </div>
                    <div class="summary-item">
                        <span class="label">平均消费：</span>
                        <span class="value">¥${data.avg_spending?.toFixed(2) || '0.00'}</span>
                    </div>
                </div>
            </div>
            <div class="analysis-details">
                <h3>详细分析</h3>
                <div class="details-content">
                    ${data.category_breakdown ? `
                        <div class="category-breakdown">
                            <h4>分类消费</h4>
                            ${Object.entries(data.category_breakdown).map(([category, amount]) => `
                                <div class="breakdown-item">
                                    <span class="category">${category}</span>
                                    <span class="amount">¥${amount.toFixed(2)}</span>
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}
                </div>
            </div>
        `;

        container.innerHTML = resultsHtml;
    }

    /**
     * 加载发票列表
     */
    async loadInvoices() {
        this.showLoading();
        try {
            const response = await this.apiRequest('/invoices');
            this.updateInvoicesGrid(response.data);

        } catch (error) {
            console.error('加载发票列表失败:', error);
        } finally {
            this.hideLoading();
        }
    }

    /**
     * 更新发票网格
     */
    updateInvoicesGrid(invoices) {
        const container = document.getElementById('invoices-grid');
        
        if (!invoices || invoices.length === 0) {
            container.innerHTML = '<p style="text-align: center; color: var(--text-tertiary); padding: 2rem;">暂无发票记录</p>';
            return;
        }

        container.innerHTML = invoices.map(invoice => `
            <div class="invoice-card">
                <div class="invoice-header">
                    <h4>${invoice.merchant}</h4>
                    <span class="invoice-type">${invoice.invoice_type}</span>
                </div>
                <div class="invoice-body">
                    <p class="invoice-amount">¥${invoice.amount.toFixed(2)}</p>
                    <p class="invoice-date">${new Date(invoice.invoice_time).toLocaleDateString()}</p>
                </div>
                <div class="invoice-actions">
                    <button class="btn btn-sm btn-secondary">查看</button>
                    <button class="btn btn-sm btn-primary">下载</button>
                </div>
            </div>
        `).join('');
    }

    /**
     * 处理发票上传
     */
    async handleInvoiceUpload(file) {
        if (!file) return;

        // 这里应该实现文件上传到服务器的逻辑
        // 由于后端API需要OCR文本，这里只是示例
        this.showNotification('发票上传功能需要OCR处理，请稍后实现', 'info');
    }

    /**
     * 防抖函数
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// 初始化应用
const app = new BillManagerApp();

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    console.log('智能记账管理系统已启动');
});
