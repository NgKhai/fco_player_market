<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\DB;

class PlayerController extends Controller
{
    public function seasons(): JsonResponse
    {
        if ($legacy = $this->legacy('/api/seasons')) {
            return $legacy;
        }

        return response()->json([
            'status' => 'success',
            'data' => DB::table('seasons')
                ->select('season_id', 'class_name', 'season_img', 'display_name')
                ->orderByDesc('season_id')->get(),
        ]);
    }

    public function search(): JsonResponse
    {
        if ($legacy = $this->legacy('/api/players/search', request()->query())) {
            return $legacy;
        }

        $keyword = trim((string) request('q', ''));
        $season = strtolower(trim((string) request('season', 'icontm')));
        $query = DB::table('players as p')
            ->leftJoin('seasons as s', 's.season_id', '=', 'p.season_id')
            ->select('p.spid as id', 'p.spid', 'p.pid', 'p.pid as uid', 'p.name_kr as name',
                's.class_name as year', 's.class_name as year_short', 'p.main_pos as pos',
                'p.main_pos as pos1', 'p.salary as attrA', 'p.ovr as attrB', 'p.salary', 'p.season_id')
            ->orderBy('p.spid');

        if ($keyword !== '') {
            $query->where(function ($q) use ($keyword) {
                $q->where('p.name_kr', 'like', "%{$keyword}%")
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

    private function legacy(string $path, array $query = []): ?JsonResponse
    {
        try {
            $response = Http::timeout(5)->get('http://127.0.0.1:8080'.$path, $query);
            return $response->successful() ? response()->json($response->json(), $response->status()) : null;
        } catch (\Throwable) {
            return null;
        }
    }
}
