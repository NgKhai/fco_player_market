<?php

namespace App\Actions;

use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Schema;

final class GarenaClient
{
    private const AUTH_URL = 'https://auth.garena.com/oauth/token/grant';
    private const MARKET_URL = 'https://fcom.garena.vn/api/market/card_price';

    public function token(): string { return $this->setting('garena_session_token'); }
    public function uid(): string { return $this->setting('garena_uid'); }
    public function connected(): bool { return strlen($this->token()) > 5; }

    public function saveToken(string $token, string $uid = ''): void
    {
        $this->saveSetting('garena_session_token', trim($token));
        if ($uid !== '') $this->saveSetting('garena_uid', trim($uid));
    }

    public function logout(): void
    {
        if (!$this->connected()) return;
        $this->saveSetting('garena_session_token', '');
        $this->saveSetting('garena_uid', '');
    }

    public function login(string $username, string $password): array
    {
        try {
            $response = Http::timeout(12)->withHeaders([
                'User-Agent' => 'Mozilla/5.0', 'Content-Type' => 'application/json',
                'Referer' => 'https://sso.garena.com/', 'Origin' => 'https://sso.garena.com',
            ])->post(self::AUTH_URL, [
                'account' => trim($username), 'password' => hash('sha256', trim($password)),
                'client_id' => '100067', 'redirect_uri' => 'https://fo4.garena.vn/', 'response_type' => 'token',
            ]);

            if (in_array($response->status(), [400, 401], true)) return [false, 'Tài khoản hoặc mật khẩu không chính xác.'];
            if (in_array($response->status(), [403, 429], true)) return [false, 'Máy chủ Garena yêu cầu xác thực Captcha/OTP. Hãy dùng tab Dán Token.'];
            $data = $response->json();
            $token = $data['access_token'] ?? $data['token'] ?? $data['sso_token'] ?? '';
            if ($token !== '') {
                $this->saveToken($token, (string) ($data['uid'] ?? $data['garena_uid'] ?? ''));
                return [true, 'Đăng nhập thành công! Đã kết nối với máy chủ Garena VN.'];
            }
        } catch (\Throwable) {
            return [false, 'Không thể kết nối đến máy chủ Garena. Bạn có thể dùng tab Dán Token.'];
        }
        return [false, 'Không nhận được phiên đăng nhập. Vui lòng dùng tab Dán Token.'];
    }

    public function playerPrices(int $spid): ?array
    {
        if (!$this->connected()) return null;
        try {
            $data = Http::timeout(8)->withHeaders([
                'Authorization' => 'Bearer '.$this->token(), 'X-GARENA-UID' => $this->uid(),
                'Referer' => 'https://fcom.garena.vn/', 'Origin' => 'https://fcom.garena.vn',
            ])->get(self::MARKET_URL, ['spid' => $spid])->json();
            if (($data['code'] ?? null) !== 0) return null;
            $prices = [];
            $rawPrices = [];
            foreach (($data['data']['prices'] ?? []) as $grade => $value) if (is_numeric($grade)) {
                $prices['vn'.(int) $grade] = $this->formatBp((int) $value);
                $rawPrices[(int) $grade] = (int) $value;
            }
            if ($prices !== null && Schema::hasTable('market_prices_vn')) {
                try {
                    foreach ($prices as $key => $formatted) {
                        $grade = (int) substr($key, 2);
                        DB::table('market_prices_vn')->updateOrInsert(
                            ['spid' => $spid, 'grade' => $grade],
                            ['price_vn' => $rawPrices[$grade] ?? 0, 'price_formatted' => $formatted, 'updated_at' => time()],
                        );
                    }
                } catch (\Throwable) {
                    // Live price remains usable when the local cache is read-only.
                }
            }
            return $prices ?: null;
        } catch (\Throwable) { return null; }
    }

    private function setting(string $key): string
    {
        if (!Schema::hasTable('app_settings')) return '';
        return (string) (DB::table('app_settings')->where('key', $key)->value('value') ?? '');
    }

    private function saveSetting(string $key, string $value): void
    {
        DB::table('app_settings')->updateOrInsert(['key' => $key], ['value' => $value, 'updated_at' => time()]);
    }

    private function formatBp(int $value): string
    {
        foreach ([[1_000_000_000, 'B', 2], [1_000_000, 'M', 1], [1_000, 'K', 1]] as [$unit, $suffix, $decimals]) {
            if ($value >= $unit) return rtrim(rtrim(number_format($value / $unit, $decimals, '.', ''), '0'), '.').$suffix;
        }
        return (string) $value;
    }
}
