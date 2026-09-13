<?php

namespace App\Actions\Players;

use Illuminate\Support\Collection;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

final class SearchPlayersAction
{
    public function execute(string $keyword, string $season): Collection
    {
        if (Schema::hasTable('fifaaddict_players')) {
            $imported = DB::table('fifaaddict_players')
                ->select('uid', 'season_code', 'name_vi', 'data_json')
                ->when($keyword !== '', fn ($q) => $q->where('name_vi', 'like', "%{$keyword}%"))
                ->when($keyword === '', fn ($q) => $q->where('season_code', $season))
                ->orderBy('name_vi')->limit(200)->get()
                ->map(function ($row) {
                    $data = json_decode($row->data_json, true) ?: [];
                    return [
                        'id' => $row->uid, 'uid' => $row->uid, 'spid' => null, 'pid' => null,
                        'name' => $row->name_vi ?: ($data['name'] ?? $row->uid),
                        'year' => $row->season_code, 'year_short' => $row->season_code,
                        'season_full' => $data['season_full'] ?? ($data['team_name'] ?? $row->season_code),
                        'team_name' => $data['team_name'] ?? null,
                        'season_id' => (int) ($data['year'] ?? 0),
                        'pos' => $data['pos1'] ?? '-', 'pos1' => $data['pos1'] ?? '-',
                        'pos2' => $data['pos2'] ?? null, 'pos1val' => (int) ($data['pos1val'] ?? 0),
                        'pos2val' => (int) ($data['pos2val'] ?? 0),
                        'attrA' => (int) ($data['attrA'] ?? 0),
                        'attrB' => (int) ($data['attrB'] ?? $data['pos1val'] ?? 0),
                        'salary' => (int) ($data['attrA'] ?? 0),
                        'foot_pref' => $data['foot_pref'] ?? 'right',
                        'foot_left' => (int) ($data['foot_left'] ?? 5),
                        'foot_right' => (int) ($data['foot_right'] ?? 5),
                        'skill_level' => (int) ($data['skill_level'] ?? 1),
                        'source_uid' => $row->uid,
                    ];
                });
            if ($imported->isNotEmpty()) return $imported;
        }

        $query = DB::table('players as p')
            ->leftJoin('seasons as s', 's.season_id', '=', 'p.season_id')
            ->select(
                'p.spid as id', 'p.spid', 'p.pid', 'p.pid as uid', 'p.name_kr as name',
                's.class_name as year', 's.class_name as year_short', 'p.main_pos as pos',
                'p.main_pos as pos1', 'p.salary as attrA', 'p.ovr as attrB', 'p.salary', 'p.season_id'
            )
            ->addSelect(['price' => DB::table('market_prices_vn')->select('price_formatted')
                ->whereColumn('market_prices_vn.spid', 'p.spid')->where('grade', 1)->limit(1)])
            ->orderBy('p.spid');

        if ($keyword !== '') {
            $query->where(function ($q) use ($keyword) {
                $q->where('p.name_kr', 'like', "%{$keyword}%")
                    ->orWhere('p.name_en', 'like', "%{$keyword}%")
                    ->orWhere('p.name_vi', 'like', "%{$keyword}%")
                    ->orWhere('p.spid', $keyword)
                    ->orWhere('p.pid', $keyword);
            });
        } else {
            $seasonKey = preg_replace('/[^a-z0-9]/', '', $season);
            $seasonKey = $seasonKey === '26ts' ? '26tots' : $seasonKey;
            $query->whereRaw("replace(lower(s.class_name), ' ', '') like ?", ["%{$seasonKey}%"]);
        }

        return $query->limit(200)->get();
    }
}
