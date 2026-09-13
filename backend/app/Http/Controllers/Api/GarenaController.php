<?php

namespace App\Http\Controllers\Api;

use App\Actions\GarenaClient;
use App\Http\Controllers\Controller;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Validation\ValidationException;

final class GarenaController extends Controller
{
    public function status(GarenaClient $client): JsonResponse
    {
        $connected = $client->connected();
        return response()->json(['status' => 'success', 'connected' => $connected, 'uid' => $connected ? $client->uid() : '']);
    }

    public function login(Request $request, GarenaClient $client): JsonResponse
    {
        try {
            $data = $request->validate(['username' => ['required', 'string', 'max:100'], 'password' => ['required', 'string', 'max:200']]);
        } catch (ValidationException $exception) {
            return response()->json(['status' => 'error', 'message' => 'Vui lòng nhập đầy đủ tài khoản và mật khẩu Garena.', 'errors' => $exception->errors()], 422);
        }
        [$success, $message] = $client->login($data['username'], $data['password']);
        return response()->json(['status' => $success ? 'success' : 'error', 'message' => $message, 'connected' => $success], $success ? 200 : 401);
    }

    public function token(Request $request, GarenaClient $client): JsonResponse
    {
        try {
            $data = $request->validate(['token' => ['required', 'string', 'min:6', 'max:4096'], 'uid' => ['nullable', 'string', 'max:100']]);
        } catch (ValidationException $exception) {
            return response()->json(['status' => 'error', 'message' => 'Token Garena không hợp lệ.', 'errors' => $exception->errors()], 422);
        }
        $client->saveToken($data['token'], $data['uid'] ?? '');
        return response()->json(['status' => 'success', 'message' => 'Đã lưu token Garena VN thành công!', 'connected' => true]);
    }

    public function logout(GarenaClient $client): JsonResponse
    {
        $client->logout();
        return response()->json(['status' => 'success', 'message' => 'Đã đăng xuất tài khoản Garena.', 'connected' => false]);
    }
}
