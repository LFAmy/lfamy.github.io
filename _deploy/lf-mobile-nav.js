/**
 * LF Academy Mobile Bottom Tab Bar v1.0
 * Auto-injects on mobile devices for teacher/student dashboards
 */
(function() {
    if (window.innerWidth > 768) return;

    // Determine which tab bar to show based on page
    var path = window.location.pathname;
    var isTeacher = path.includes('teacher') || path.includes('admin');
    var isStudent = path.includes('student') || path.includes('app') || path.includes('kids');
    var isParent = path.includes('parent');

    var tabs = [];

    if (isTeacher) {
        tabs = [
            { icon: '\ud83c\udfe0', label: '\u4e3b\u9801', href: 'teacher-dashboard.html', active: path.includes('dashboard') },
            { icon: '\ud83d\udc65', label: '\u5b78\u751f', href: 'teacher-class-monitor.html', active: path.includes('class') || path.includes('monitor') },
            { icon: '\ud83d\udcdd', label: '\u51fa\u5377', href: 'smart-test-gen.html', active: path.includes('test') || path.includes('gen') },
            { icon: '\ud83d\udcca', label: '\u5831\u544a', href: 'parent-report-gen.html', active: path.includes('report') },
            { icon: '\u2699\ufe0f', label: '\u8a2d\u5b9a', href: 'admin-members.html', active: path.includes('admin') || path.includes('member') }
        ];
    } else if (isParent) {
        tabs = [
            { icon: '\ud83c\udfe0', label: '\u4e3b\u9801', href: 'parent-center.html', active: path.includes('center') },
            { icon: '\ud83d\udcc8', label: '\u9032\u5ea6', href: 'student-journey.html', active: path.includes('journey') || path.includes('progress') },
            { icon: '\ud83d\udcdd', label: '\u7df4\u7fd2', href: 'homework-tracker.html', active: path.includes('homework') },
            { icon: '\ud83d\udce3', label: '\u5831\u544a', href: 'post-trial-report.html', active: path.includes('report') || path.includes('trial') },
            { icon: '\ud83d\udcac', label: '\u806f\u7d61', href: 'parent-comms.html', active: path.includes('comms') }
        ];
    } else if (isStudent) {
        tabs = [
            { icon: '\ud83c\udfe0', label: '\u4e3b\u9801', href: 'app.html', active: path.includes('app') },
            { icon: '\ud83c\udfaf', label: '\u7df4\u7fd2', href: 'trap-quiz.html', active: path.includes('quiz') || path.includes('trap') },
            { icon: '\u2694\ufe0f', label: 'Boss', href: 'kids-boss-battle.html', active: path.includes('boss') },
            { icon: '\ud83c\udfc6', label: '\u52f3\u7ae0', href: 'achievement-wall.html', active: path.includes('achieve') || path.includes('badge') },
            { icon: '\ud83d\udc64', label: '\u6211', href: 'student-platform.html', active: path.includes('platform') }
        ];
    }

    if (!tabs.length) return;

    // Create nav element
    var nav = document.createElement('nav');
    nav.className = 'lf-mobile-nav';
    nav.innerHTML = tabs.map(function(t) {
        var cls = t.active ? ' class="active"' : '';
        return '<a href="' + t.href + '"' + cls + '><span class="icon">' + t.icon + '</span><span>' + t.label + '</span></a>';
    }).join('');
    document.body.appendChild(nav);

    console.log('[LF Mobile Nav] Tab bar injected for ' + (isTeacher ? 'teacher' : isParent ? 'parent' : 'student'));
})();