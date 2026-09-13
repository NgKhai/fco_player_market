<?php

namespace Tests\Feature;

use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Schema;
use Tests\TestCase;

class GarenaTest extends TestCase
{
    protected function setUp(): void
    {
        parent::setUp();
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
            'https://auth.garena.com/*' => Http::response(['access_token' => 'oauth-token', 'uid' => '456'], 200),
        ]);

        $this->postJson('/api/garena/login', ['username' => 'test-user', 'password' => 'test-password'])
            ->assertOk()
            ->assertJson(['status' => 'success', 'connected' => true]);

        $this->getJson('/api/garena/status')->assertJson(['connected' => true, 'uid' => '456']);
    }
}
