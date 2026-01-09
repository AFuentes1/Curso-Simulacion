#lang racket
;; ------------------------------------------------------------
;; Cómo ejecutar este archivo
;;        https://racket-lang.org/download/
;;        $env:PATH += ";C:\Program Files\Racket\"
;;        racket GenerateRacket1_20.rkt
;; ------------------------------------------------------------

(define (generar-numeros-1-20 cantidad)
  (build-list cantidad (λ (_) (+ 1 (random 20)))))

(define n 1000000)

(call-with-output-file "racket_u01.txt"
  (λ (archivo)
    (for ([x (generar-numeros-1-20 n)])
      (fprintf archivo "~a\n" x)))
  #:exists 'replace)
