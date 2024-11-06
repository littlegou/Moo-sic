document.addEventListener('DOMContentLoaded', () => {
    const daysContainer = document.querySelector('.days');
    const monthYearInput = document.querySelector('.date-input');
    const gotoButton = document.querySelector('.goto-btn');
    const todayButton = document.querySelector('.today-btn');
    const prevButton = document.querySelector('.prev');
    const nextButton = document.querySelector('.next');

    let currentMonth = new Date().getMonth();
    let currentYear = new Date().getFullYear();
    let selectedDate;

    function createElement(tag, className) {
        const element = document.createElement(tag);
        if (className) {
            element.classList.add(className);
        }
        return element;
    }

    function renderCalendar(month, year) {
        daysContainer.innerHTML = '';
        const date = new Date(year, month);
        const totalDays = new Date(year, month + 1, 0).getDate();
        const startDay = new Date(year, month, 1).getDay();

        document.querySelector('.date').textContent = date.toLocaleString('default', { month: 'long' }) + ' ' + year;

        const eventDay = document.querySelector('.event-day');
        const eventDate = document.querySelector('.event-date');
        if (selectedDate) {
            eventDay.textContent = selectedDate.toLocaleString('default', { weekday: 'short' });
            eventDate.textContent = selectedDate.toLocaleString('default', { day: 'numeric' }) + ' ' + selectedDate.toLocaleString('default', { month: 'long' }) + ' ' + selectedDate.getFullYear();
        }

        for (let i = 0; i < startDay; i++) {
            const emptyBox = createElement('div', 'empty');
            daysContainer.appendChild(emptyBox);
        }

        for (let i = 1; i <= totalDays; i++) {
            const dayElement = createElement('div', 'day');
            dayElement.textContent = i;

            if (selectedDate && i === selectedDate.getDate() && month === selectedDate.getMonth() && year === selectedDate.getFullYear()) {
                dayElement.classList.add('selected');
            }

            dayElement.addEventListener('click', () => {
                if (selectedDate) {
                    const previousSelectedDay = document.querySelector('.selected');
                    if (previousSelectedDay) previousSelectedDay.classList.remove('selected');
                }

                selectedDate = new Date(year, month, i);
                let selecteddatefordb = year + "-" + month + "-" + i
                console.log(selecteddatefordb);
                eventDay.textContent = selectedDate.toLocaleString('default', { weekday: 'short' });
                eventDate.textContent = selectedDate.toLocaleString('default', { day: 'numeric' }) + ' ' + selectedDate.toLocaleString('default', { month: 'long' }) + ' ' + selectedDate.getFullYear();
                dayElement.classList.add('selected');
                fetchEventsForSelectedDate(selecteddatefordb);
            });

            daysContainer.appendChild(dayElement);
        }
        loadmooods();
    }

    function fetchEventsForSelectedDate(selecteddatefordb) {
        const dateStr = selecteddatefordb;
        fetch(`/events?date=${dateStr}`)
            .then(response => response.json())
            .then(data => {
                console.log(data);
                const noDataContainer = document.getElementById('noDataContainer');
                const eventDataContainer = document.getElementById('eventDataContainer');
                const eventDetails = document.getElementById('eventDetails');
                const goToOtherPageButton = document.getElementById('goToOtherPage');
    
                if (data != null)  {
                    eventDetails.innerHTML = '';
                    data.forEach(events => {
                        const eventItem = document.createElement('div');
                        const embedContainer = document.createElement('div');
                        const resizedEmbed = events.embed
                        .replace('width="560"', 'width="250"')
                        .replace('height="315"', 'height="140"');
                        embedContainer.innerHTML = resizedEmbed;
                        eventItem.appendChild(embedContainer);
                        const songInfo = document.createElement('p');
                        songInfo.textContent = `${events.song_name} by ${events.artist}`;
                        eventItem.appendChild(songInfo);
                        const desc = document.createElement('p');
                        desc.textContent = `บรรยายความรู้สึก : ${events.description}`
                        eventItem.appendChild(desc)
                        eventDetails.appendChild(eventItem);
                    });
                    eventDataContainer.style.display = 'block';
                    noDataContainer.style.display = 'none';
                } else {
                    eventDataContainer.style.display = 'none';
                    noDataContainer.style.display = 'block';

                    const url = `/selectmoodforcalendar?date=${dateStr}`;
                    goToOtherPageButton.onclick = () => {
                        window.location.href = url;
                    };
                }
            });
    }
    function loadmooods() {
        fetch('/mooods')
            .then(response => response.json())
            .then(data => {
                const days = document.querySelectorAll('.days .day');
    
                data.moods.forEach(mood => {
                    const eventDate = new Date(mood.date);
                    const dayOfMonth = eventDate.getDate();
                    const month = eventDate.getMonth();
                    const year = eventDate.getFullYear();
    
                    if (month === currentMonth && year === currentYear) {
                        const dayElement = days[dayOfMonth - 1];
                        dayElement.style.border = 'none';

                        const img = document.createElement('img', 'day');
                        dayElement.innerHTML = '';
                        img.src = `../static/images/${mood.moodimg}`;
                        img.style.width = '145%';
                        img.style.height = '145%';
                        img.style.objectFit = 'contain';
                        
    
                        dayElement.appendChild(img);
                    }
                });
            });
    }

    prevButton.addEventListener('click', () => {
        currentMonth -= 1;
        if (currentMonth < 0) {
            currentMonth = 11;
            currentYear -= 1;
        }
        renderCalendar(currentMonth, currentYear);
    });

    nextButton.addEventListener('click', () => {
        currentMonth += 1;
        if (currentMonth > 11) {
            currentMonth = 0;
            currentYear += 1;
        }
        renderCalendar(currentMonth, currentYear);
    });

    gotoButton.addEventListener('click', () => {
        const [month, year] = monthYearInput.value.split('/').map(num => parseInt(num, 10));
        if (!isNaN(month) && !isNaN(year)) {
            currentMonth = month - 1;
            currentYear = year;
            renderCalendar(currentMonth, currentYear);
        } else {
            alert('Please enter a valid month and year in mm/yyyy format.');
        }
    });

    todayButton.addEventListener('click', () => {
        const today = new Date();
        currentMonth = today.getMonth();
        currentYear = today.getFullYear();
        renderCalendar(currentMonth, currentYear);
    });

    renderCalendar(currentMonth, currentYear);
});