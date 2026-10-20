package dev.esweb.travel;

import co.elastic.clients.elasticsearch._types.ElasticsearchException;
import co.elastic.clients.transport.TransportException;
import java.io.IOException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@RestControllerAdvice
public class ApiErrors {
    public record ErrorBody(String code, String message) {
    }

    @ExceptionHandler({MethodArgumentNotValidException.class, HttpMessageNotReadableException.class})
    ResponseEntity<ErrorBody> invalidInput(Exception error) {
        return ResponseEntity.badRequest().body(new ErrorBody("INVALID_SEARCH_INPUT",
                "请检查关键词、两位大写城市编码、整数分预算和坐标/半径；所有字段必填。"));
    }

    @ExceptionHandler({IOException.class, TransportException.class})
    ResponseEntity<ErrorBody> unavailable(Exception error) {
        return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body(new ErrorBody("SEARCH_UNAVAILABLE",
                "搜索连接暂不可用，请检查本机 ES 与服务端端点，再重试。"));
    }

    @ExceptionHandler(ElasticsearchException.class)
    ResponseEntity<ErrorBody> rejected(ElasticsearchException error) {
        return ResponseEntity.status(HttpStatus.BAD_GATEWAY).body(new ErrorBody("SEARCH_BACKEND_REJECTED",
                "ES 拒绝搜索，请在本机核对本课索引、mapping 与服务端配置。"));
    }

    @ExceptionHandler(AttractionSearchService.IncompleteSearchException.class)
    ResponseEntity<ErrorBody> incomplete(Exception error) {
        return ResponseEntity.status(HttpStatus.BAD_GATEWAY).body(new ErrorBody("SEARCH_INCOMPLETE",
                "搜索未完整完成或结果字段不符合契约，请检查 ES 与本课资料后重试。"));
    }
}
