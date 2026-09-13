<?php

use App\Http\Controllers\Api\PlayerController;
use Illuminate\Support\Facades\Route;

Route::get('/seasons', [PlayerController::class, 'seasons']);
Route::get('/players/search', [PlayerController::class, 'search']);
Route::get('/players/detail', [PlayerController::class, 'detail']);
Route::get('/garena/status', fn () => response()->json(['status' => 'success', 'connected' => false, 'uid' => '']));
Route::match(['post'], '/garena/{action}', fn (string $action) => response()->json([
    'status' => 'error', 'message' => 'Garena integration chưa được migrate sang Laravel.', 'connected' => false,
], 501))->whereIn('action', ['login', 'token', 'logout']);
