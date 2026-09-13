<?php

namespace Tests\Feature;

use Illuminate\Database\Schema\Blueprint;
use Illuminate\Http\Client\Factory;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Schema;
use Illuminate\Support\Facades\DB;
use App\Actions\GarenaClient;
use Tests\TestCase;

class GarenaTest extends TestCase
{
    protected function setUp(): void
    {
        parent::setUp();
        Http::swap(new Factory);
        Schema::dropIfExists('app_settings');
        Schema::create('app_settings', function (Blueprint $table): void {
            $table->string('key')->primary();
            $table->text('value')->nullable();
            $table->integer('updated_at')->nullable();
        });
    }

    public function test_manual_token_is_saved_without_returning_it(): void
    {
        $this->postJson('/api/garena/token', ['token' => 'test-session-token', 'uid' => '123'])
            ->assertOk()
            ->assertJson(['status' => 'success', 'connected' => true])
            ->assertJsonMissing(['token' => 'test-session-token']);

        $this->getJson('/api/garena/status')->assertJson(['connected' => true, 'uid' => '123']);
    }

    public function test_login_stores_garena_session_from_oauth_response(): void
    {
        Http::fake([
            'https://auth.garena.com/api/prelogin*' => Http::response(['v1' => 'one', 'v2' => 'two'], 200),
            'https://auth.garena.com/api/login*' => Http::response(['redirect_uri' => 'https://fo4.garena.vn/'], 200),
            'https://auth.garena.com/oauth/token/grant' => Http::response(['redirect_uri' => 'https://fo4.garena.vn/#access_token=oauth-token&uid=456'], 200),
        ]);

        $this->postJson('/api/garena/login', ['username' => 'test-user', 'password' => 'test-password'])
            ->assertOk()
            ->assertJson(['status' => 'success', 'connected' => true]);

        $this->getJson('/api/garena/status')->assertJson(['connected' => true, 'uid' => '456']);
    }

    public function test_bearer_prefix_is_normalized_and_live_prices_keep_metadata(): void
    {
        Schema::create('market_prices_vn', function (Blueprint $table): void {
            $table->integer('spid');
            $table->integer('grade');
            $table->integer('price_vn')->default(0);
            $table->string('price_formatted')->nullable();
            $table->integer('updated_at')->nullable();
            $table->primary(['spid', 'grade']);
        });
        Http::fake([
            'https://fcom.garena.vn/*' => Http::response(['code' => 0, 'data' => ['prices' => ['1' => 1250000]]], 200),
        ]);

        $client = app(GarenaClient::class);
        $client->saveToken('Bearer test-session-token', '123');
        $prices = $client->playerPrices(1001);

        $this->assertSame('Garena VN (Live)', $prices['source']);
        $this->assertSame('1.3M', $prices['vn1']);
        Http::assertSent(fn ($request): bool => $request->header('Authorization') === ['Bearer test-session-token']);
        $this->assertSame('1.3M', DB::table('market_prices_vn')->value('price_formatted'));
    }
}
