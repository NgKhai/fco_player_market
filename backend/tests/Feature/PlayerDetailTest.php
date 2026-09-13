<?php

namespace Tests\Feature;

use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;
use Tests\TestCase;

class PlayerDetailTest extends TestCase
{
    protected function setUp(): void
    {
        parent::setUp();
        Schema::dropIfExists('players');
        Schema::dropIfExists('seasons');
        Schema::create('seasons', function (Blueprint $table): void {
            $table->integer('season_id')->primary();
            $table->string('class_name')->nullable();
            $table->string('display_name')->nullable();
        });
        Schema::create('players', function (Blueprint $table): void {
            $table->integer('spid')->primary();
            $table->integer('pid')->nullable();
            $table->integer('season_id')->nullable();
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
}
