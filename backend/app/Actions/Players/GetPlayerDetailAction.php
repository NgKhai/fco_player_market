<?php

namespace App\Actions\Players;

use Illuminate\Support\Facades\DB;

final class GetPlayerDetailAction
{
    public function execute(?string $uid, ?int $spid): ?array
    {
        $normalizedUid = preg_replace('/^pid/i', '', (string) $uid);
        $value = $spid ?: (ctype_digit($normalizedUid) ? (int) $normalizedUid : 0);

        $row = DB::table('players as p')
            ->leftJoin('seasons as s', 's.season_id', '=', 'p.season_id')
            ->where(fn ($q) => $q->where('p.spid', $value)->orWhere('p.pid', $value))
            ->select('p.*', 's.class_name', 's.display_name')
            ->first();

        if (!$row) {
            return null;
        }

        $db = [
            'id' => $row->spid, 'spid' => $row->spid, 'pid' => $row->pid,
            'uid' => (string) $row->pid, 'name' => $row->name_kr ?: (string) $row->pid,
            'year' => $row->class_name ?: 'FO4', 'year_short' => $row->class_name ?: 'FO4',
            'pos' => $row->main_pos ?: '-', 'pos1' => $row->main_pos ?: '-',
            'attrA' => $row->salary ?: 0, 'attrB' => $row->ovr ?: 0, 'salary' => $row->salary ?: 0,
            'current_ovr' => $row->ovr ?: '-', 'season_full' => $row->class_name ?: 'FO4',
            'season_name' => $row->display_name ?: ($row->class_name ?: 'FO4'),
            'bodytype_name' => '-', 'height' => $row->height ?: '-', 'weight' => $row->weight ?: '-',
            'foot_pref' => $row->foot_pref ?: 'right', 'team_name' => $row->team_name ?: '-',
        ];

        $prices = DB::table('market_prices_vn')->where('spid', $row->spid)
            ->orderBy('grade')->get()->mapWithKeys(fn ($price) => [(string) $price->grade => $price->price_vn])->all();

        return [
            'db' => $db, 'price' => $prices, 'traits' => [], 'source' => 'SQLite local',
            'garena_connected' => false, 'active_server' => 'LOCAL',
        ];
    }
}
