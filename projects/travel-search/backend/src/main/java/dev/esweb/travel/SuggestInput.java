package dev.esweb.travel;

import jakarta.validation.constraints.*;
import com.fasterxml.jackson.annotation.JsonIgnore;

public record SuggestInput(
        @NotBlank @Size(max = 60) String q,
        @NotNull @Pattern(regexp = "BJ|SY") String cityCode,
        @NotNull @Pattern(regexp = "completion|sayt|pinyin|exact|fuzzy|guarded") String mode) {
    @JsonIgnore
    @AssertTrue(message = "拼音模式只接收2至40个ASCII英文字母")
    public boolean isPinyinValid() {
        return !"pinyin".equals(mode) || q != null && q.strip().matches("[A-Za-z]{2,40}");
    }
}
