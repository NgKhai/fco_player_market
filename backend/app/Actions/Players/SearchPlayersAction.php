<?php

namespace App\Actions\Players;

use Illuminate\Support\Collection;
use Illuminate\Support\Facades\DB;

final class SearchPlayersAction
{
    public function execute(string $keyword, string $season): Collection
    {
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
