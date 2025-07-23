function getCookie(name) {
  const value = document.cookie
    .split('; ')
    .find(row => row.startsWith(name + '='))
  return value ? decodeURIComponent(value.split('=')[1]) : null;
}

console.log(getCookie('MoodleSession'));

// bu kodu moodledan çalıştırın ve konsoldan MoodleSession değerini alın