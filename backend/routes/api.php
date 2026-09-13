<?php

use App\Http\Controllers\Api\PlayerController;
use App\Http\Controllers\Api\GarenaController;
use Illuminate\Support\Facades\Route;

Route::get('/seasons', [PlayerController::class, 'seasons']);
Route::get('/players/search', [PlayerController::class, 'search']);
Route::get('/players/detail', [PlayerController::class, 'detail']);
Route::get('/garena/status', [GarenaController::class, 'status']);
Route::post('/garena/login', [GarenaController::class, 'login']);
Route::post('/garena/token', [GarenaController::class, 'token']);
Route::post('/garena/logout', [GarenaController::class, 'logout']);
