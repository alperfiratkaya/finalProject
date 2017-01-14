<div id="master-container">
  <div id="form-container">
    <div class="container" id="tabs-container">

      <div class="left-col" id="toolbox-col" style="padding-top: 30px">

        <ul class="nav-tabs" role="tablist">
          <li class="active toolbox-tab" data-target="#add-field">Alan Ekle</li>
          <li class="toolbox-tab" data-target="#field-settings">Alan özellikleri</li>
          <li class="toolbox-tab" data-target="#form-settings">Form özellikleri</li>
        </ul>

        <div class="tab-content">

          <div class="tab-pane active" style="padding: 30px;" id="add-field">

            <div class="col-sm-6">
              <button class="btn-primary new-element" data-type="element-single-line-text" style="width: 100%;">Tek Satırlık Yazı Alani</button>
              <button class="btn-primary new-element" data-type="element-paragraph-text" style="width: 100%;">Paragraf Alanı</button>
              <button class="btn-primary new-element" data-type="element-multiple-choice" style="width: 100%;">Çok Seçenekli Alan</button>
              <button class="btn-primary grey new-element" data-type="element-section-break" style="width: 100%;">Alan Belirtici</button>
              <button class="btn-primary new-element" data-type="element-number" style="width: 100%;">Sayı Alani</button>
              <button class="btn-primary new-element" data-type="element-checkboxes" style="width: 100%;">Onay Kutusu</button>
              <button class="btn-primary new-element" data-type="element-dropdown" style="width: 100%;">Seçim Menüsü</button>
            </div>

            <div style="clear:both"></div>
          </div>

          <div class="tab-pane" id="field-settings" style="padding: 20px; display: none; margin: 5px;">

            <div class="section">
              <div class="form-group">
                <label>Alan Etiketi</label>
                <input type="text" class="form-control" id="field-label" value="Untitled" />
              </div>
            </div>

            <div class="section" id="field-choices" style="display: none;">
              <div class="form-group">
                <label>Seçenekler</label>
              </div>
            </div>

            <div class="section" id="field-options">

              <div class="form-group">
                <label>Alan Özellikleri</label>
              </div>

              <div class="field-options">
                <div class="checkbox">
                  <label>
                    <input type="checkbox" id="required">Zorunlu Alan
                  </label>
                </div>
              </div>

            </div>

            <div class="section" id="field-description">

              <div class="form-group">
                <label>Alan Açıklaması</label>
              </div>

              <div class="field-description">
                <textarea id="description"></textarea>
              </div>

            </div>

            <div><button class="btn-danger" id="control-remove-field" style="margin-left:2cm;">Kaldır</button>
            <button class="btn-success" id="control-add-field" style="margin-left:2cm;">Alanı Ekle</button></div>

          </div>

          <div class="tab-pane" id="form-settings" style="padding: 20px; display: none">

            <div class="section">
              <div class="form-group">
                <label>Başlık</label>
                <input type="text" class="bind-control form-control" data-bind="#form-title-label" id="form-title" value="" />
              </div>

              <div class="form-group">
                <label>Açıklama</label>
                <textarea class="bind-control form-control" data-bind="#form-description-label" id="form-description"></textarea>
              </div>
            </div>

          </div>

        </div>

      </div>

      <div class="right-col" id="form-col">

        <div class="loading">
          Loading...
        </div>

      </div>

      <div style="clear: both"></div>

    </div> <!-- /container -->
  </div>

  <div style="clear: both"></div>

</div>

<div style="clear: both"></div>