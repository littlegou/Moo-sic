document.addEventListener("DOMContentLoaded", function() {
    const moodWheel = document.querySelector('.mood-wheel');
    const moods = document.querySelectorAll('.mood');
    const reasonsList = document.querySelector('.reasons-list');
    const reasonsContainer = document.querySelector('.reasons-container');

    let startX, scrollLeft;

    // ฟังก์ชันจับตำแหน่งเริ่มต้นการเลื่อน
    moodWheel.addEventListener('mousedown', (e) => {
        startX = e.pageX - moodWheel.offsetLeft;
        scrollLeft = moodWheel.scrollLeft;
        moodWheel.classList.add('active');
    });

    // ฟังก์ชันสำหรับการเลื่อนซ้ายขวาเมื่อเคลื่อนเมาส์
    moodWheel.addEventListener('mousemove', (e) => {
        if (!startX) return; // หากไม่ได้เริ่มการเลื่อน ให้หยุดการทำงาน
        e.preventDefault();
        const x = e.pageX - moodWheel.offsetLeft;
        const walk = (x - startX) * 2; // ความเร็วการเลื่อน
        moodWheel.scrollLeft = scrollLeft - walk;
    });

    // รีเซ็ตการเลื่อนเมื่อเมาส์ถูกปล่อย
    moodWheel.addEventListener('mouseleave', () => startX = null);
    moodWheel.addEventListener('mouseup', () => startX = null);

    // สร้างเหตุผลเมื่อเลือก mood
    moods.forEach(mood => {
        mood.addEventListener('click', function() {
            moods.forEach(m => m.classList.remove('selected')); // ลบการเลือกจาก mood อื่น
            this.classList.add('selected'); // เพิ่มการเลือกให้ mood ปัจจุบัน
            const selectedMood = this.dataset.mood;
            updateReasons(selectedMood); // อัปเดตเหตุผลตาม mood ที่เลือก
        });
    });

    // อัปเดตเหตุผลตาม mood ที่เลือก
    // อัปเดตเหตุผลตาม mood ที่เลือก
function updateReasons(mood) {
    const reasons = {
        Happy: ['รู้สึกพอใจ', 'รู้สึกซาบซึ้ง', 'รู้สึกเติมเต็ม', 'รู้สึกยินดี'],
        Sad: ['อกหัก', 'ท้อแท้', 'หดหู่', 'เศร้าซึม'],
        Excited: ['เร้าใจ', 'ประหม่า', 'คาดหวัง', 'ท้าทาย'],
        Inspiration: ['เกี่ยวกับความรัก', 'มีเป้าหมาย', 'อยากเชื่อมั่นในตนเอง', 'อยากจะเริ่มต้นใหม่'],
        Angry: ['เดือดดาล', 'อารมณ์เสีย', 'เคียดแค้น', 'ประชดประชัน'],
    };
    
    reasonsList.innerHTML = ''; // ล้างรายการเหตุผลก่อนหน้า
    if (reasons[mood]) {
        // แสดง container สำหรับเหตุผล
        reasonsContainer.style.display = 'block';

        reasons[mood].forEach(reason => {
            const reasonItem = document.createElement('div');
            reasonItem.textContent = reason;
            reasonItem.classList.add('reason-item');
            reasonsList.appendChild(reasonItem);

            // คลิกที่เหตุผลเพื่อนำไปยังหน้าถัดไป
            reasonItem.addEventListener('click', function() {
                window.location.href = `randomsong?mood=${mood}&reason=${reason}`;
            });
        });
        } else {
            // ถ้าไม่มีเหตุผลให้ซ่อน container
            reasonsContainer.style.display = 'none';
        }
    }

});
