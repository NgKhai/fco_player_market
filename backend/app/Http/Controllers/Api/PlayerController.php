<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use Illuminate\Http\JsonResponse;
use App\Actions\Players\GetPlayerDetailAction;
use App\Actions\Players\ListSeasonsAction;
use App\Actions\Players\SearchPlayersAction;
use App\Http\Requests\Api\PlayerDetailRequest;
use App\Http\Requests\Api\PlayerSearchRequest;

class PlayerController extends Controller
{
    public function seasons(ListSeasonsAction $action): JsonResponse
    {
        return response()->json(['status' => 'success', 'data' => $action->execute()]);
    }

    public function search(PlayerSearchRequest $request, SearchPlayersAction $action): JsonResponse
    {
        $data = $request->validated();
        $players = $action->execute($data['q'] ?? '', strtolower(trim($data['season'] ?? 'icontm')));
        return response()->json(['status' => 'success', 'total' => $players->count(), 'data' => $players]);
    }

    public function detail(PlayerDetailRequest $request, GetPlayerDetailAction $action): JsonResponse
    {
        $data = $request->validated();
        $player = $action->execute($data['uid'] ?? null, isset($data['spid']) ? (int) $data['spid'] : null);

        if ($player === null) {
            return response()->json(['status' => 'error', 'message' => 'Player not found', 'data' => null], 404);
        }

        return response()->json(['status' => 'success', 'data' => $player]);
    }
}
