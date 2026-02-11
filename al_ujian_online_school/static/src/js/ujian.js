(function() {
    'use strict';

    var isSaving = false;

    function initUjian() {
        if (typeof window.ujianData === 'undefined') {
            return;
        }

        var timerElement = document.getElementById('timer-text');
        var remainingTime = window.ujianData.remainingTime;
        var timerContainer = document.getElementById('timer');

        if (!timerElement || !timerContainer) {
            return;
        }

        function updateTimer() {
            if (remainingTime <= 0) {
                var submitForm = document.querySelector('form[action*="/submit"]');
                if (submitForm) submitForm.submit();
                return;
            }

            var hours = Math.floor(remainingTime / 3600);
            var minutes = Math.floor((remainingTime % 3600) / 60);
            var seconds = remainingTime % 60;

            var timeString = '';
            if (hours > 0) {
                timeString = hours.toString().padStart(2, '0') + ':';
            }
            timeString += minutes.toString().padStart(2, '0') + ':' + seconds.toString().padStart(2, '0');

            timerElement.textContent = timeString;

            if (remainingTime <= 60) {
                timerContainer.classList.remove('warning');
                timerContainer.classList.add('danger');
            } else if (remainingTime <= 300) {
                timerContainer.classList.add('warning');
            }

            remainingTime--;
        }

        updateTimer();
        setInterval(updateTimer, 1000);

        function getAnswerData() {
            var answerData = {
                is_ragu: document.getElementById('ragu_checkbox')?.checked || false
            };

            if (window.ujianData.tipeSoal === 'pg' || window.ujianData.tipeSoal === 'benar_salah') {
                var selectedRadio = document.querySelector('input[name="pilihan"]:checked');
                if (selectedRadio) {
                    answerData.pilihan_id = parseInt(selectedRadio.value);
                }
            } else if (window.ujianData.tipeSoal === 'pg_kompleks') {
                var selectedCheckboxes = document.querySelectorAll('input[name="pilihan_kompleks"]:checked');
                answerData.pilihan_ids = Array.from(selectedCheckboxes).map(function(cb) {
                    return parseInt(cb.value);
                });
            } else if (window.ujianData.tipeSoal === 'isian') {
                var isianInput = document.getElementById('jawaban_isian');
                if (isianInput) {
                    answerData.jawaban = isianInput.value;
                }
            } else if (window.ujianData.tipeSoal === 'essay') {
                var essayInput = document.getElementById('jawaban_essay');
                if (essayInput) {
                    answerData.jawaban = essayInput.value;
                }
            }

            return answerData;
        }

        function saveAnswerAsync() {
            if (isSaving) return;
            isSaving = true;

            var answerData = getAnswerData();

            fetch('/my/ujian/' + window.ujianData.pesertaId + '/save', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    jsonrpc: '2.0',
                    method: 'call',
                    params: {
                        peserta_id: window.ujianData.pesertaId,
                        jawaban_id: window.ujianData.jawabanId,
                        answer_data: answerData
                    }
                })
            }).then(function(response) {
                return response.json();
            }).then(function(data) {
                isSaving = false;
                if (data.result && data.result.success) {
                    updateNavItem();
                }
            }).catch(function() {
                isSaving = false;
            });
        }

        function updateNavItem() {
            var currentNav = document.querySelector('.soal-nav-item.active');
            if (currentNav) {
                var hasAnswer = false;
                if (window.ujianData.tipeSoal === 'pg' || window.ujianData.tipeSoal === 'benar_salah') {
                    hasAnswer = !!document.querySelector('input[name="pilihan"]:checked');
                } else if (window.ujianData.tipeSoal === 'pg_kompleks') {
                    hasAnswer = document.querySelectorAll('input[name="pilihan_kompleks"]:checked').length > 0;
                } else if (window.ujianData.tipeSoal === 'isian') {
                    hasAnswer = !!document.getElementById('jawaban_isian')?.value;
                } else if (window.ujianData.tipeSoal === 'essay') {
                    hasAnswer = !!document.getElementById('jawaban_essay')?.value;
                }

                currentNav.classList.toggle('answered', hasAnswer);
                currentNav.classList.toggle('ragu', document.getElementById('ragu_checkbox')?.checked || false);
            }
        }

        document.querySelectorAll('input[name="pilihan"]').forEach(function(radio) {
            radio.addEventListener('change', saveAnswerAsync);
        });

        document.querySelectorAll('input[name="pilihan_kompleks"]').forEach(function(checkbox) {
            checkbox.addEventListener('change', saveAnswerAsync);
        });

        var isianInput = document.getElementById('jawaban_isian');
        if (isianInput) {
            var isianTimeout;
            isianInput.addEventListener('input', function() {
                clearTimeout(isianTimeout);
                isianTimeout = setTimeout(saveAnswerAsync, 1000);
            });
            isianInput.addEventListener('blur', saveAnswerAsync);
        }

        var essayInput = document.getElementById('jawaban_essay');
        if (essayInput) {
            var essayTimeout;
            essayInput.addEventListener('input', function() {
                clearTimeout(essayTimeout);
                essayTimeout = setTimeout(saveAnswerAsync, 2000);
            });
            essayInput.addEventListener('blur', saveAnswerAsync);
        }

        var raguCheckbox = document.getElementById('ragu_checkbox');
        if (raguCheckbox) {
            raguCheckbox.addEventListener('change', saveAnswerAsync);
        }

        document.querySelectorAll('.soal-nav-item').forEach(function(link) {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                var href = link.getAttribute('href');
                if (href) {
                    window.location.href = href;
                }
            });
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(initUjian, 100);
        });
    } else {
        setTimeout(initUjian, 100);
    }

    document.addEventListener('ujianDataReady', function() {
        setTimeout(initUjian, 50);
    });
})();
