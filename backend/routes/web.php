<?php

use Illuminate\Support\Facades\Route;
use Symfony\Component\HttpFoundation\BinaryFileResponse;

Route::get('/', function () {
    return file_get_contents(base_path('../web/static/index.html'));
});

Route::get('/app.js', function () {
    return file_get_contents(base_path('../web/static/app.js'));
});

Route::get('/style.css', function () {
    return file_get_contents(base_path('../web/static/style.css'));
});

Route::get('/minifaces/{path}', function (string $path): BinaryFileResponse {
    abort_if(str_contains($path, '..'), 404);
    $file = realpath(base_path('../output/minifaces/'.$path));
    $root = realpath(base_path('../output/minifaces'));
    abort_if(!$file || !$root || !str_starts_with($file, $root.DIRECTORY_SEPARATOR) || !is_file($file), 404);
    return response()->file($file, ['Cache-Control' => 'public, max-age=86400']);
})->where('path', '.*');
