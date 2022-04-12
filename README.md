<strong>Микроблог Flask</strong><br />
-----------------------------------------------------------------------------------------------------------------------------------------------------------
<br />
Перед запуском сервера, в переменные окружения необходимо проставить настройки почтового сервера:<br /><br />
<code>$ export MAIL_SERVER=...</code><br />
<code>$ export MAIL_PORT=...</code><br />
<code>$ export MAIL_USE_TLS=...</code><br />
<code>$ export MAIL_USERNAME...</code><br />
<code>$ export MAIL_PASSWORD=...</code><br /><br />


Установка и запуск:<br />
<ol>
<li><i>Клонировать репозиторий.</li>
<li>Создать виртуальное окружение.</li>
<li>Установить зависимости из файла requirements.txt</li>
<li>flask run</li>
</ol><br />

-----------------------------------------------------------------------------------------------------------------------------------------------------------
<code><b>v0.1</b></code><br /><ul><li>Реализована домашняя страница.</li><li>Реализована форма регистрации пользователей.</li><li>Реализована система авторизации пользоваталей.</li><li>Реализована кнопка выхода из системы авторизованного пользователя.</li></ul><br />
 <code><b>v0.2</b></code><br /><br /><ul><li>Реализована форма редактирования данных страницы пользователя.</li><li>Реализованы аватары.</li><li>Реализован показ времени последнего посещения.</li></ul><br />
 <code><b>v0.3</b></code><br /><br /><ul><li>Реализована система подписчиков и подписок.</li></ul><br />
 <code><b>v0.4</b></code><br /><br /><ul><li>Реализована система пагинации, когда сообщений на странице становится больше, заданного в config-файле проекта количества.</li><li>Реализована страница с лентой сообщений пользователей в блоге.</li><li>Реализована страница с личными сообщениями. </li></ul><br />
<code><b>v0.5</b></code><br /><br /><ul><li>Реализована система сброса пароля и восстановления доступа к аккаунту посредством отправки сообщения на электронный адрес.<br /></li></ul><br />
<code><b>v0.6</b></code><br /><br /><ul><li>Реализован Фронтенд с Bootstrap.</li><li>Добавлена отправка приветственного сообщения на электронную почту после успешной регистрации.</li></ul><br />

