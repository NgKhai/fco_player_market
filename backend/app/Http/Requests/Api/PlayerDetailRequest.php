<?php

namespace App\Http\Requests\Api;

use Illuminate\Foundation\Http\FormRequest;

class PlayerDetailRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'uid' => ['nullable', 'string', 'max:30', 'required_without:spid'],
            'spid' => ['nullable', 'integer', 'min:1', 'required_without:uid'],
        ];
    }
}
