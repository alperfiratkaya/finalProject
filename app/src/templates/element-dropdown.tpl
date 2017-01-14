<li class="form-element {#required}required{/required}" id="element-{position}" data-label="{label}" data-position="{position}" data-type="element-dropdown">
	<label>
		<span class="label-title">{label}</span>
		{#required}<span class="required-star"> *</span>{/required}
	</label>
	<select style="width: 50%" class="choices" data-type="settings-dropdown" disabled>
		<option class="option-1" val="First Choice" selected><span class="choice-label">Birinci Seçenek</span></option>
		<option class="option-2" val="Second Choice"><span class="choice-label">İkinci Seçenek</span></option>
		<option class="option-3" val="Third Choice"><span class="choice-label">Üçüncü Seçenek</span></option>
	</select>
</li>