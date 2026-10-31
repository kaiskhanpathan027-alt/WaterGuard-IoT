/**
 * Water Quality Monitoring System - Core Interactive Scripts
 */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Mobile Menu Toggle
    const navToggle = document.getElementById('navToggle');
    const navLinks = document.getElementById('navLinks');
    if (navToggle && navLinks) {
        navToggle.addEventListener('click', function () {
            navLinks.classList.toggle('show');
        });
    }

    // 2. Demo Login Autofill Helpers with Custom Usernames
    window.fillDemoAccount = function (role) {
        const inputField = document.getElementById('login_input');
        const passField = document.getElementById('password');
        if (!inputField || !passField) return;

        if (role === 'kais') {
            inputField.value = 'kais.khan@water.guard';
            passField.value = 'kais123';
        } else if (role === 'rajeshwar') {
            inputField.value = 'rajeshwar.gaurkar@water.guard';
            passField.value = 'rajeshwar123';
        } else if (role === 'admin') {
            inputField.value = 'admin.director@water.guard';
            passField.value = 'admin123';
        } else {
            inputField.value = 'alex.turner@water.guard';
            passField.value = 'student123';
        }

        // Highlight fields gently
        inputField.style.borderColor = '#0284c7';
        passField.style.borderColor = '#0284c7';
        setTimeout(() => {
            inputField.style.borderColor = '';
            passField.style.borderColor = '';
        }, 1200);
    };

    // 3. Client-side Live Real-Time Analyzer (Used on New Test & Home Page Calculator)
    const phInput = document.getElementById('ph_input');
    const tdsInput = document.getElementById('tds_input');
    const turbInput = document.getElementById('turbidity_input');

    if (phInput && tdsInput && turbInput) {
        const updateAnalysisPreview = () => {
            const ph = parseFloat(phInput.value) || 7.0;
            const tds = parseFloat(tdsInput.value) || 200.0;
            const turb = parseFloat(turbInput.value) || 1.0;

            const preview = evaluateWaterClient(ph, tds, turb);
            renderPreviewUI(preview);
        };

        phInput.addEventListener('input', updateAnalysisPreview);
        tdsInput.addEventListener('input', updateAnalysisPreview);
        turbInput.addEventListener('input', updateAnalysisPreview);

        // Initial trigger
        updateAnalysisPreview();
    }

    // Helper client-side calculator matching backend scientific model
    function evaluateWaterClient(ph, tds, turb) {
        // pH evaluation
        let phStatus = 'Safe';
        let phScore = 90;
        let phDesc = 'Optimal drinking range';
        if (ph < 6.0 || ph > 9.0) {
            phStatus = 'Unsafe';
            phScore = 30;
            phDesc = ph < 6.0 ? 'Highly acidic & corrosive' : 'Caustic & bitter alkalinity';
        } else if (ph < 6.5 || ph > 8.5) {
            phStatus = 'Moderate';
            phScore = 60;
            phDesc = ph < 6.5 ? 'Mildly acidic' : 'Mildly alkaline';
        }

        // TDS evaluation
        let tdsStatus = 'Safe';
        let tdsScore = 90;
        let tdsDesc = 'Ideal mineral balance';
        if (tds > 900) {
            tdsStatus = 'Unsafe';
            tdsScore = 25;
            tdsDesc = 'Excessive dissolved solids (>900 mg/L)';
        } else if (tds > 500) {
            tdsStatus = 'Moderate';
            tdsScore = 65;
            tdsDesc = 'Elevated hardness (500-900 mg/L)';
        }

        // Turbidity evaluation
        let turbStatus = 'Safe';
        let turbScore = 95;
        let turbDesc = 'Crystal clear (<=5 NTU)';
        if (turb > 10.0) {
            turbStatus = 'Unsafe';
            turbScore = 25;
            turbDesc = 'High turbidity / cloudy (>10 NTU)';
        } else if (turb > 5.0) {
            turbStatus = 'Moderate';
            turbScore = 65;
            turbDesc = 'Slight murkiness (5-10 NTU)';
        }

        // Weighted WQI
        const wqi = Math.round((phScore * 0.35) + (tdsScore * 0.35) + (turbScore * 0.30));

        let overall = 'Safe';
        let color = '#10b981';
        let badgeClass = 'badge-safe';

        if (phStatus === 'Unsafe' || tdsStatus === 'Unsafe' || turbStatus === 'Unsafe' || wqi < 50) {
            overall = 'Unsafe';
            color = '#ef4444';
            badgeClass = 'badge-unsafe';
        } else if (phStatus === 'Moderate' || tdsStatus === 'Moderate' || turbStatus === 'Moderate' || wqi < 75) {
            overall = 'Moderate';
            color = '#f59e0b';
            badgeClass = 'badge-moderate';
        }

        return {
            overall,
            color,
            badgeClass,
            wqi,
            ph: { status: phStatus, desc: phDesc },
            tds: { status: tdsStatus, desc: tdsDesc },
            turb: { status: turbStatus, desc: turbDesc }
        };
    }

    function renderPreviewUI(p) {
        const previewBadge = document.getElementById('preview_badge');
        const previewWqi = document.getElementById('preview_wqi');
        const previewCircle = document.getElementById('preview_circle');

        if (previewBadge) {
            previewBadge.className = `badge ${p.badgeClass}`;
            previewBadge.innerHTML = `<span class="pulse-dot"></span> ${p.overall}`;
        }

        if (previewWqi) {
            previewWqi.textContent = p.wqi;
            previewWqi.style.color = p.color;
        }

        if (previewCircle) {
            previewCircle.style.borderColor = p.color;
        }

        // Mini status indicators
        const miniPh = document.getElementById('mini_ph_status');
        const miniTds = document.getElementById('mini_tds_status');
        const miniTurb = document.getElementById('mini_turb_status');

        if (miniPh) {
            miniPh.textContent = `${p.ph.status} (${p.ph.desc})`;
            miniPh.className = `text-${p.ph.status.toLowerCase()}`;
        }
        if (miniTds) {
            miniTds.textContent = `${p.tds.status} (${p.tds.desc})`;
            miniTds.className = `text-${p.tds.status.toLowerCase()}`;
        }
        if (miniTurb) {
            miniTurb.textContent = `${p.turb.status} (${p.turb.desc})`;
            miniTurb.className = `text-${p.turb.status.toLowerCase()}`;
        }
    }

    // 4. Delete Confirmation modal / alert
    window.confirmDelete = function (msg) {
        return confirm(msg || "Are you sure you want to permanently delete this record?");
    };
});
