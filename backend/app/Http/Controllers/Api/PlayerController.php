<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\DB;

class PlayerController extends Controller
{
    public function seasons(): JsonResponse
    {
        return response()->json([
            'status' => 'success',
            'data' => DB::table('seasons')
                ->select('season_id', 'class_name', 'season_img', 'display_name')
                ->orderByDesc('season_id')->get(),
        ]);
    }

    public function search(): JsonResponse
    {
        $keyword = trim((string) request('q', ''));
        $season = strtolower(trim((string) request('season', 'icontm')));
        $query = DB::table('players as p')
            ->leftJoin('seasons as s', 's.season_id', '=', 'p.season_id')
            ->select('p.spid as id', 'p.spid', 'p.pid', 'p.pid as uid', 'p.name_kr as name',
                's.class_name as year', 's.class_name as year_short', 'p.main_pos as pos',
                'p.main_pos as pos1', 'p.salary as attrA', 'p.ovr as attrB', 'p.salary', 'p.season_id')
            ->addSelect(['price' => DB::table('market_prices_vn')->select('price_formatted')
                ->whereColumn('market_prices_vn.spid', 'p.spid')->where('grade', 1)->limit(1)])
            ->orderBy('p.spid');

        if ($keyword !== '') {
            $query->where(function ($q) use ($keyword) {
                $q->where('p.name_kr', 'like', "%{$keyword}%")
                    ->orWhere('p.name_en', 'like', "%{$keyword}%")
                    ->orWhere('p.name_vi', 'like', "%{$keyword}%")
                    ->orWhere('p.spid', $keyword)->orWhere('p.pid', $keyword);
            });
        } else {
            $seasonKey = preg_replace('/[^a-z0-9]/', '', $season);
            $seasonKey = $seasonKey === '26ts' ? '26tots' : $seasonKey;
            $query->whereRaw("replace(lower(s.class_name), ' ', '') like ?", ["%{$seasonKey}%"]);
        }

        $players = $query->limit(200)->get();
        return response()->json(['status' => 'success', 'total' => $players->count(), 'data' => $players]);
    }

    public function detail(): JsonResponse
    {
        $uid = preg_replace('/^pid/i', '', (string) request('uid', ''));
        $spid = (string) request('spid', '');
        if (!ctype_digit($uid) && !ctype_digit($spid)) {
            return response()->json(['status' => 'error', 'message' => 'Missing uid parameter'], 400);
        }

        $value = (int) ($spid ?: $uid);
        $row = DB::table('players as p')
            ->leftJoin('seasons as s', 's.season_id', '=', 'p.season_id')
            ->where(fn ($q) => $q->where('p.spid', $value)->orWhere('p.pid', $value))
            ->select('p.*', 's.class_name', 's.display_name')
            ->first();

        if (!$row) {
            return response()->json(['status' => 'success', 'data' => null]);
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

        return response()->json([
            'status' => 'success',
            'data' => ['db' => $db, 'price' => $prices, 'traits' => [], 'source' => 'SQLite local',
                'garena_connected' => false, 'active_server' => 'LOCAL'],
        ]);
    }
}
