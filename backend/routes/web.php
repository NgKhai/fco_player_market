<?php

use Illuminate\Support\Facades\Route;

Route::get('/', function () {
    return file_get_contents(base_path('../web/static/index.html'));
});

Route::get('/app.js', function () {
    return file_get_contents(base_path('../web/static/app.js'));
});

Route::get('/style.css', function () {
    return file_get_contents(base_path('../web/static/style.css'));
});
