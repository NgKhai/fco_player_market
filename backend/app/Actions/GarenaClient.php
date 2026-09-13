<?php

namespace App\Actions;

use GuzzleHttp\Cookie\CookieJar;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Schema;

final class GarenaClient
{
    private const AUTH_BASE_URL = 'https://auth.garena.com';
    private const APP_ID = 100067;
    private const MARKET_URL = 'https://fcom.garena.vn/api/market/card_price';

    public function token(): string { return $this->setting('garena_session_token'); }
    public function uid(): string { return $this->setting('garena_uid'); }
    public function connected(): bool { return strlen($this->token()) > 5; }

    public function saveToken(string $token, string $uid = ''): void
    {
        $this->saveSetting('garena_session_token', preg_replace('/^\s*(?:Bearer\s+|(?:sso_token|access_token)\s*=\s*)/i', '', trim($token)) ?: '');
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
            $cookies = new CookieJar();
            $headers = [
                'User-Agent' => 'Mozilla/5.0', 'Content-Type' => 'application/json',
                'Referer' => 'https://sso.garena.com/', 'Origin' => 'https://sso.garena.com',
            ];
            $request = Http::timeout(12)->withOptions(['cookies' => $cookies])->withHeaders($headers);
            $account = trim($username);
            $prelogin = $request->get(self::AUTH_BASE_URL.'/api/prelogin', [
                'app_id' => self::APP_ID, 'account' => $account,
            ]);
            $preloginData = $prelogin->json() ?: [];
            if (!$prelogin->successful() || !empty($preloginData['error'])) {
                return $this->loginError($prelogin->status(), $preloginData['error'] ?? null);
            }

            $encryptedPassword = $this->encryptPassword(trim($password), $preloginData['v1'] ?? '', $preloginData['v2'] ?? '');
            if ($encryptedPassword === '') return [false, 'Không nhận được thông tin xác thực từ máy chủ Garena.'];

            $login = $request->get(self::AUTH_BASE_URL.'/api/login', [
                'app_id' => self::APP_ID, 'account' => $account, 'password' => $encryptedPassword,
                'redirect_uri' => 'https://fo4.garena.vn/',
            ]);
            $loginData = $login->json() ?: [];
            if (!$login->successful() || !empty($loginData['error'])) {
                return $this->loginError($login->status(), $loginData['error'] ?? null);
            }

            $grant = $request->post(self::AUTH_BASE_URL.'/oauth/token/grant', [
                'client_id' => self::APP_ID, 'response_type' => 'token',
                'redirect_uri' => 'https://fo4.garena.vn/',
            ]);
            $data = $grant->json() ?: [];
            $data = array_merge($data, $this->redirectData($data['redirect_uri'] ?? ''));
            if (!$grant->successful() || !empty($data['error'])) {
                return $this->loginError($grant->status(), $data['error'] ?? null);
            }
            $token = $data['access_token'] ?? $data['token'] ?? $data['sso_token'] ?? $data['session_key'] ?? '';
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
            $prices = ['source' => 'Garena VN (Live)', 'server' => 'VN', 'updatetime' => date('Y-m-d H:i')];
            $rawPrices = [];
            foreach (range(1, 10) as $grade) {
                $value = $data['data']['prices'][(string) $grade] ?? 0;
                if (!is_numeric($value)) continue;
                $prices['vn'.$grade] = $this->formatBp((int) $value);
                $rawPrices[$grade] = (int) $value;
            }
            if (count($rawPrices) && Schema::hasTable('market_prices_vn')) {
                try {
                    foreach ($prices as $key => $formatted) {
                        if (!preg_match('/^vn(\d+)$/', $key, $match)) continue;
                        $grade = (int) $match[1];
                        DB::table('market_prices_vn')->updateOrInsert(
                            ['spid' => $spid, 'grade' => $grade],
                            ['price_vn' => $rawPrices[$grade] ?? 0, 'price_formatted' => $formatted, 'updated_at' => time()],
                        );
                    }
                } catch (\Throwable) {
                    // Live price remains usable when the local cache is read-only.
                }
            }
            return count($rawPrices) ? $prices : null;
        } catch (\Throwable) { return null; }
    }

    private function encryptPassword(string $password, mixed $v1, mixed $v2): string
    {
        if ($v1 === '' || $v2 === '' || !function_exists('openssl_encrypt')) return '';
        $md5 = md5($password);
        $key = hex2bin(hash('sha256', hash('sha256', $md5.$v1).$v2));
        $encrypted = openssl_encrypt(hex2bin($md5), 'AES-256-ECB', $key, OPENSSL_RAW_DATA | OPENSSL_ZERO_PADDING);
        return $encrypted === false ? '' : bin2hex($encrypted);
    }

    private function redirectData(string $redirectUri): array
    {
        if ($redirectUri === '') return [];
        $query = [];
        $fragment = [];
        parse_str((string) parse_url($redirectUri, PHP_URL_QUERY), $query);
        parse_str((string) parse_url($redirectUri, PHP_URL_FRAGMENT), $fragment);
        return array_merge($query, $fragment);
    }

    private function loginError(int $status, ?string $error): array
    {
        if (in_array($status, [400, 401], true) || $error === 'error_auth') return [false, 'Tài khoản hoặc mật khẩu không chính xác.'];
        if (in_array($status, [403, 429], true) || str_contains((string) $error, 'captcha')) return [false, 'Máy chủ Garena yêu cầu xác thực Captcha/OTP. Hãy dùng tab Dán Token.'];
        return [false, 'Không thể hoàn tất đăng nhập Garena. Bạn có thể dùng tab Dán Token.'];
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
        return $value > 0 ? (string) $value : '-';
    }
}
