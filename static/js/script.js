document.addEventListener("DOMContentLoaded", function() {
    const moodWheel = document.querySelector('.mood-wheel');
    const moods = document.querySelectorAll('.mood');
    const reasonsList = document.querySelector('.reasons-list');
    const reasonsContainer = document.querySelector('.reasons-container');

    let startX, scrollLeft;

    moodWheel.addEventListener('mousedown', (e) => {
        startX = e.pageX - moodWheel.offsetLeft;
        scrollLeft = moodWheel.scrollLeft;
        moodWheel.classList.add('active');
    });

    moodWheel.addEventListener('mousemove', (e) => {
        if (!startX) return;
        e.preventDefault();
        const x = e.pageX - moodWheel.offsetLeft;
        const walk = (x - startX) * 2;
        moodWheel.scrollLeft = scrollLeft - walk;
    });

    moodWheel.addEventListener('mouseleave', () => startX = null);
    moodWheel.addEventListener('mouseup', () => startX = null);

    moods.forEach(mood => {
        mood.addEventListener('click', function() {
            moods.forEach(m => m.classList.remove('selected'));
            this.classList.add('selected');
            const selectedMood = this.dataset.mood;
            updateReasons(selectedMood);
        });
    });

function updateReasons(mood) {
    const reasons = {
        Happy: ['รู้สึกพอใจ', 'รู้สึกซาบซึ้ง', 'รู้สึกเติมเต็ม', 'รู้สึกยินดี'],
        Sad: ['อกหัก', 'ท้อแท้', 'หดหู่', 'เศร้าซึม'],
        Excited: ['เร้าใจ', 'ประหม่า', 'คาดหวัง', 'ท้าทาย'],
        Inspiration: ['เกี่ยวกับความรัก', 'มีเป้าหมาย', 'อยากเชื่อมั่นในตนเอง', 'อยากจะเริ่มต้นใหม่'],
        Angry: ['เดือดดาล', 'อารมณ์เสีย', 'เคียดแค้น', 'ประชดประชัน'],
    };
    
    reasonsList.innerHTML = '';
    if (reasons[mood]) {
        reasonsContainer.style.display = 'block';

        reasons[mood].forEach(reason => {
            const reasonItem = document.createElement('div');
            reasonItem.textContent = reason;
            reasonItem.classList.add('reason-item');
            reasonsList.appendChild(reasonItem);

            reasonItem.addEventListener('click', function() {
                window.location.href = `randomsong?mood=${mood}&reason=${reason}`;
            });
        });
        } else {
            reasonsContainer.style.display = 'none';
        }
    }

});
