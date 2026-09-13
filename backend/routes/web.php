<?php

use Illuminate\Support\Facades\Route;
use Symfony\Component\HttpFoundation\BinaryFileResponse;

Route::get('/', function () {
    return response(file_get_contents(base_path('../web/static/index.html')))
        ->header('Content-Type', 'text/html; charset=UTF-8');
});

Route::get('/app.js', function () {
    return response(file_get_contents(base_path('../web/static/app.js')))
        ->header('Content-Type', 'application/javascript; charset=UTF-8');
});

Route::get('/style.css', function () {
    return response(file_get_contents(base_path('../web/static/style.css')))
        ->header('Content-Type', 'text/css; charset=UTF-8');
});

Route::get('/seasons/{file}', function (string $file): BinaryFileResponse {
    abort_unless((bool) preg_match('/^season_\d+\.png$/', $file), 404);
    $path = realpath(base_path('../output/seasons/'.$file));
    abort_unless($path && is_file($path), 404);
    return response()->file($path, ['Cache-Control' => 'public, max-age=86400']);
});

Route::get('/minifaces/{path}', function (string $path): BinaryFileResponse {
    abort_if(str_contains($path, '..'), 404);
    $file = realpath(base_path('../output/minifaces/'.$path));
    $root = realpath(base_path('../output/minifaces'));
    abort_if(!$file || !$root || !str_starts_with($file, $root.DIRECTORY_SEPARATOR) || !is_file($file), 404);
    return response()->file($file, ['Cache-Control' => 'public, max-age=86400']);
})->where('path', '.*');
