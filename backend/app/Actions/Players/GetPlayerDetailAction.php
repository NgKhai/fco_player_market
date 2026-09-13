<?php

namespace App\Actions\Players;

use App\Actions\GarenaClient;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

final class GetPlayerDetailAction
{
    public function __construct(private readonly GarenaClient $garena) {}

    public function execute(?string $uid, ?int $spid): ?array
    {
        $normalizedUid = preg_replace('/^pid/i', '', (string) $uid);
        if ($spid === null && $normalizedUid !== '' && Schema::hasTable('fifaaddict_players')) {
            $source = DB::table('fifaaddict_players')->where('uid', $normalizedUid)->first();
            if ($source) {
                $data = json_decode($source->data_json, true) ?: [];
                return [
                    'db' => array_merge($data, ['id' => $source->uid, 'uid' => $source->uid,
                        'name' => $source->name_vi ?: ($data['name'] ?? $source->uid),
                        'year_short' => $source->season_code, 'season_id' => (int) ($data['year'] ?? 0)]),
                    'price' => $data['price'] ?? [], 'traits' => $data['traits'] ?? [],
                    'source' => 'FIFAAddict SQLite', 'garena_connected' => false, 'active_server' => 'LOCAL',
                ];
            }
        }
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

        $prices = Schema::hasTable('market_prices_vn')
            ? DB::table('market_prices_vn')->where('spid', $row->spid)
                ->orderBy('grade')->get()->mapWithKeys(fn ($price) => [(string) $price->grade => $price->price_formatted ?: $price->price_vn])->all()
            : [];
        $livePrices = $this->garena->playerPrices((int) $row->spid);
        $priceVn = $livePrices;
        if ($livePrices !== null) $prices = array_combine(
            array_map(fn (string $key): string => (string) ((int) substr($key, 2)), array_keys($livePrices)),
            array_values($livePrices),
        );

        return [
            'db' => $db, 'price' => $prices, 'price_vn' => $priceVn, 'traits' => [], 'source' => 'SQLite local',
            'garena_connected' => $this->garena->connected(), 'active_server' => $livePrices !== null ? 'VN' : 'LOCAL',
        ];
    }
}
