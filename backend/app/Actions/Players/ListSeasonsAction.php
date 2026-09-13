<?php

namespace App\Actions\Players;

use Illuminate\Support\Collection;
use Illuminate\Support\Facades\DB;

final class ListSeasonsAction
{
    public function execute(): Collection
    {
        return DB::table('seasons')
            ->select('season_id', 'class_name', 'season_img', 'display_name')
            ->orderByDesc('season_id')
            ->get();
    }
}
