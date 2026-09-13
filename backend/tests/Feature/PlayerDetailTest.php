<?php

namespace Tests\Feature;

use Illuminate\Database\Schema\Blueprint;
use Illuminate\Http\Client\Factory;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Schema;
use Tests\TestCase;

class PlayerDetailTest extends TestCase
{
    protected function setUp(): void
    {
        parent::setUp();
        Http::swap(new Factory);
        Schema::dropIfExists('players');
        Schema::dropIfExists('seasons');
        Schema::dropIfExists('market_prices_vn');
        Schema::dropIfExists('app_settings');
        Schema::create('seasons', function (Blueprint $table): void {
            $table->integer('season_id')->primary();
            $table->string('class_name')->nullable();
            $table->string('display_name')->nullable();
        });
        Schema::create('app_settings', function (Blueprint $table): void {
            $table->string('key')->primary();
            $table->text('value')->nullable();
            $table->integer('updated_at')->nullable();
        });
        Schema::create('players', function (Blueprint $table): void {
            $table->integer('spid')->primary();
            $table->integer('pid')->nullable();
            $table->integer('season_id')->nullable();
            $table->string('name_kr')->nullable();
            $table->string('main_pos')->nullable();
            $table->integer('salary')->nullable();
            $table->integer('ovr')->nullable();
            $table->integer('height')->nullable();
            $table->integer('weight')->nullable();
            $table->string('foot_pref')->nullable();
            $table->string('team_name')->nullable();
        });
    }

    public function test_unknown_spid_returns_not_found_error(): void
    {
        $this->getJson('/api/players/detail?spid=999999999')
            ->assertNotFound()
            ->assertJson([
                'status' => 'error',
                'message' => 'Player not found',
                'data' => null,
            ]);
    }

    public function test_unknown_uid_returns_not_found_error(): void
    {
        $this->getJson('/api/players/detail?uid=missing-player')
            ->assertNotFound()
            ->assertJsonPath('status', 'error');
    }

    public function test_detail_uses_local_prices_when_live_market_is_unavailable(): void
    {
        Schema::create('market_prices_vn', function (Blueprint $table): void {
            $table->integer('spid');
            $table->integer('grade');
            $table->integer('price_vn')->default(0);
            $table->string('price_formatted')->nullable();
            $table->integer('updated_at')->nullable();
            $table->primary(['spid', 'grade']);
        });
        DB::table('seasons')->insert(['season_id' => 1, 'class_name' => 'ICON', 'display_name' => 'ICON']);
        DB::table('players')->insert(['spid' => 1001, 'pid' => 1, 'season_id' => 1, 'name_kr' => 'Test', 'main_pos' => 'ST']);
        DB::table('market_prices_vn')->insert(['spid' => 1001, 'grade' => 1, 'price_vn' => 1000000, 'price_formatted' => '1M']);
        DB::table('app_settings')->insert(['key' => 'garena_session_token', 'value' => 'test-token']);
        Http::fake(['https://fcom.garena.vn/*' => Http::response([], 503)]);

        $this->getJson('/api/players/detail?spid=1001')
            ->assertOk()
            ->assertJsonPath('data.price.1', '1M')
            ->assertJsonPath('data.active_server', 'LOCAL')
            ->assertJsonPath('data.garena_connected', true);
    }
}
