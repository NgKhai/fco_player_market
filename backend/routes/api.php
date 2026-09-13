<?php

use App\Http\Controllers\Api\PlayerController;
use Illuminate\Support\Facades\Route;
use Illuminate\Support\Facades\Http;

Route::get('/seasons', [PlayerController::class, 'seasons']);
Route::get('/players/search', [PlayerController::class, 'search']);

// Temporary bridge while the remaining Python integrations are migrated.
Route::match(['get', 'post'], '/{path}', function (string $path) {
    try {
        $url = 'http://127.0.0.1:8080/api/'.$path;
        $request = Http::timeout(8);
        if (request()->isMethod('post')) {
            $request = $request->withBody(request()->getContent(), request()->header('Content-Type', 'application/json'));
        }
        $response = $request->send(request()->method(), $url, ['query' => request()->query()]);
        return response()->json($response->json(), $response->status());
    } catch (\Throwable $e) {
        return response()->json(['status' => 'error', 'message' => 'Legacy API unavailable'], 502);
    }
})->where('path', '.*');
